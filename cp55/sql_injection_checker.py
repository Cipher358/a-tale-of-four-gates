import pprint


def split_sections(method):
    sections = {}
    current_section = list()
    current_section_name = "start"
    sections[current_section_name] = current_section
    previous_section_name = None

    in_pswitch_data = False
    for line in method:
        if line.startswith(":"):
            if not in_pswitch_data:
                sections[current_section_name] = current_section
                current_section = list()
                previous_section_name = current_section_name
                current_section_name = line
            else:
                current_section.append(line)

            if line.startswith(":goto") and (
                    previous_section_name.startswith(":pswitch") or previous_section_name.startswith(":sswitch")) \
                    and sections[previous_section_name][-1] == "nop":
                sections[previous_section_name][-1] = "goto " + current_section_name

        elif line.startswith(".param") or line.startswith(".line") or line.startswith(".locals"):
            continue
        else:
            if line.startswith(".packed-switch"):
                in_pswitch_data = True
            elif line == ".end packed-switch":
                in_pswitch_data = False
            current_section.append(line)

    sections[current_section_name] = current_section

    sections = {key: value for (key, value) in sections.items()
                if not key.startswith(":try") and not key.startswith(":catch")}

    return sections


class SqlInjectionChecker:

    def __init__(self, apk_handler):
        self.apk_handler = apk_handler

    def check_insert(self, method):
        sections = split_sections(method)

        visited_sections = set()
        visited_sections.add("start")

        execution_paths = list()
        execution_paths.append(sections["start"])

        while visited_sections != set(sections.keys()):
            new_execution_paths = list()
            while len(execution_paths) > 0:
                path = execution_paths.pop(0)

                lines_in_section = len(path)
                new_path = list()
                for i in range(0, lines_in_section):
                    line = path.pop(0)

                    if line.startswith("if"):
                        # if-test vA, vB, +CCCC
                        # if-testz vAA, +BBBB

                        tokens = line.split()
                        if_cond = tokens[0]
                        first_register = tokens[1].replace(",", "")
                        dest_branch = tokens[-1]

                        if if_cond.endswith("z"):
                            second_register = str(0)
                        else:
                            second_register = tokens[2].replace(",", "")

                        true_path = list(new_path)
                        false_path = list(new_path)

                        if if_cond == "if-eq" or if_cond == "if-eqz":
                            true_path.append("c: " + first_register + " == " + second_register)
                            false_path.append("c: " + first_register + " != " + second_register)
                        elif if_cond == "if-ne" or if_cond == "if-nez":
                            true_path.append("c: " + first_register + " != " + second_register)
                            false_path.append("c: " + first_register + " == " + second_register)
                        elif if_cond == "if-lt" or if_cond == "if-ltz":
                            true_path.append("c: " + first_register + " < " + second_register)
                            false_path.append("c: " + first_register + " >= " + second_register)
                        elif if_cond == "if-ge" or if_cond == "if-gez":
                            true_path.append("c: " + first_register + " >= " + second_register)
                            false_path.append("c: " + first_register + " < " + second_register)
                        elif if_cond == "if-gt" or if_cond == "if-gtz":
                            true_path.append("c: " + first_register + " > " + second_register)
                            false_path.append("c: " + first_register + " <= " + second_register)
                        elif if_cond == "if-le" or if_cond == "if-lez":
                            true_path.append("c: " + first_register + " <= " + second_register)
                            false_path.append("c: " + first_register + " > " + second_register)

                        true_path.extend(sections[dest_branch])
                        false_path.extend(path)

                        new_execution_paths.append(true_path)
                        new_execution_paths.append(false_path)

                        visited_sections.add(dest_branch)
                        break

                    elif line.startswith("goto"):
                        # goto +AA
                        # goto/16 +AAAA
                        # goto/32 +AAAAAAAA
                        target_branch = line.split()[-1]

                        new_path.extend(sections[target_branch])
                        new_execution_paths.append(new_path)

                        visited_sections.add(target_branch)

                    elif line.startswith("sparse-switch"):
                        # sparse-switch vAA, +BBBBBBBB
                        sparse_switch_tokens = line.split()
                        register_to_test = sparse_switch_tokens[1].replace(",", "")
                        switch_table_offset = sparse_switch_tokens[-1]
                        switch_table_section = sections[switch_table_offset]

                        default_condition = []
                        for switch_table_entry in switch_table_section:
                            # 0x1 -> :sswitch_0
                            entry_tokens = switch_table_entry.split()
                            register_value = entry_tokens[0]
                            target_branch = entry_tokens[-1]
                            if target_branch in sections.keys():
                                default_condition.append("" + register_to_test + " != " + register_value)
                                switch_path = list(new_path)
                                switch_path.append("c: " + register_to_test + " == " + register_value)
                                switch_path.extend(sections[target_branch])
                                new_execution_paths.append(switch_path)
                                visited_sections.add(target_branch)

                        # the default path is taken when no switch condition is met
                        default_path = list(new_path)
                        default_path.append("c: " + " && ".join(default_condition))
                        default_path.extend(path)
                        new_execution_paths.append(default_path)

                        visited_sections.add(switch_table_offset)
                        break

                    elif line.startswith("packed-switch"):
                        # packed-switch vAA, +BBBBBBBB
                        packed_switch_tokens = line.split()
                        register_to_test = packed_switch_tokens[1].replace(",", "")
                        switch_table_offset = packed_switch_tokens[-1]
                        switch_table_section = sections[switch_table_offset]

                        index = 0
                        first_case_value = None
                        for switch_table_entry in switch_table_section:
                            if switch_table_entry.startswith(".packed-switch"):
                                first_case_value = int(switch_table_entry.split()[1], 0)
                            elif switch_table_entry in sections.keys():
                                switch_path = list(new_path)
                                switch_path.append("c: " + register_to_test + " == " + str(index + first_case_value))
                                switch_path.extend(sections[switch_table_entry])
                                index = index + 1
                                new_execution_paths.append(switch_path)
                                visited_sections.add(switch_table_entry)

                        # the default path is taken when no switch condition is met
                        default_path = list(new_path)
                        default_path.append("c: " + register_to_test + " < " + str(first_case_value) + " && " +
                                            register_to_test + " >= " + str(index + first_case_value))
                        default_path.extend(path)
                        new_execution_paths.append(default_path)

                        visited_sections.add(switch_table_offset)
                        break
                    else:
                        new_path.append(line)

                if len(new_path) == lines_in_section:
                    new_execution_paths.append(new_path)

            execution_paths = new_execution_paths

        print(len(execution_paths))
        pprint.pp(execution_paths)

