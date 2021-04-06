import pprint


class SqlInjectionChecker:

    def __init__(self):
        a = 0

    def split_sections(self, method):
        sections = {}
        current_section = list()
        current_section_name = "start"
        sections[current_section_name] = current_section

        for line in method:
            if line.startswith(":") and not line.startswith(":try"):
                sections[current_section_name] = current_section
                current_section = list()
                current_section_name = line
            else:
                current_section.append(line)

        sections[current_section_name] = current_section

        return sections

    def check_insert(self, method):
        sections = self.split_sections(method)

        visited_sections = set()
        visited_sections.add("start")

        execution_paths = list()
        execution_paths.append((list(), sections["start"]))

        while len(visited_sections) <= 22:
            new_execution_paths = list()
            while len(execution_paths) > 0:
                constraints, path = execution_paths.pop(0)

                lines_in_section = len(path)
                new_path = list()
                for i in range(0, lines_in_section):
                    line = path.pop(0)

                    if line.startswith("if"):
                        dest_branch = line.split()[-1]

                        true_path = list(new_path)
                        true_constraints = list(constraints)
                        true_path.extend(sections[dest_branch])
                        true_constraints.append((i, line))

                        false_constraints = list(constraints)
                        false_constraints.append((i, "not(" + line + ")"))
                        false_path = list(new_path)
                        for j in range(i + 1, lines_in_section):
                            line = path.pop(0)
                            false_path.append(line)

                        new_execution_paths.append((true_constraints, true_path))
                        new_execution_paths.append((false_constraints, false_path))

                        visited_sections.add(dest_branch)
                        break

                    elif line.startswith("goto"):
                        dest_branch = line.split()[-1]

                        new_path.extend(sections[dest_branch])
                        new_execution_paths.append((constraints, new_path))

                        visited_sections.add(dest_branch)
                    elif line.startswith(".catch"):
                        dest_branch = line.split()[-1]

                        new_path.extend(sections[dest_branch])
                        # new_execution_paths.append((constraints, new_path))

                        visited_sections.add(dest_branch)
                    elif line.startswith("sparse-switch"):
                        fst_tokens = line.split()

                        fst_dest_branch = fst_tokens[-1]

                        switch_section = sections[fst_dest_branch]
                        for switch_line in switch_section:
                            tokens = switch_line.split()
                            snd_dest_branch = tokens[-1]
                            if snd_dest_branch in sections.keys():
                                switch_path = list(new_path)
                                switch_constraints = list(constraints)
                                switch_constraints.append((i, line + " // " + switch_line))
                                switch_path.extend(sections[snd_dest_branch])
                                new_execution_paths.append((switch_constraints, switch_path))
                            visited_sections.add(snd_dest_branch)
                        visited_sections.add(fst_dest_branch)
                    else:
                        new_path.append(line)

                if len(new_path) == lines_in_section:
                    new_execution_paths.append((constraints, new_path))

            execution_paths = new_execution_paths

        pprint.pp(execution_paths)


def run():
    method = [".locals 5",
              "const/4 v0, 0x0",
              "if-nez p2, :cond_0",
              "return-object v0",
              ".line 1",
              ":cond_0",
              ":try_start_0",
              "iget-object v1, p0, Lcom/moe/pushlibrary/providers/MoEProvider;->a:Lcom/moe/pushlibrary/providers/b;",
              "invoke-virtual {v1}, Landroid/database/sqlite/SQLiteOpenHelper;->getWritableDatabase()Landroid/database/sqlite/SQLiteDatabase;",
              "move-result-object v1",
              ".line 2",
              "invoke-virtual {p0, v1}, Lcom/moe/pushlibrary/providers/MoEProvider;->b(Landroid/database/sqlite/SQLiteDatabase;)V",
              ".line 3",
              "sget-object v2, Lcom/moe/pushlibrary/providers/MoEProvider;->b:Landroid/content/UriMatcher;",
              "invoke-virtual {v2, p1}, Landroid/content/UriMatcher;->match(Landroid/net/Uri;)I",
              "move-result v2",
              "const-wide/16 v3, 0x0",
              "sparse-switch v2, :sswitch_data_0",
              ".line 4",
              "new-instance p2, Ljava/lang/StringBuilder;",
              "goto/16 :goto_0",
              ":sswitch_0",
              "const-string v2, \"CARDS\"",
              ".line 5",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 6",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moengage/core/n0/a;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto/16 :goto_1",
              ":sswitch_1",
              "const-string v2, \"INAPP_STATS\"",
              ".line 7",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 8",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$i;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto/16 :goto_1",
              ":sswitch_2",
              "const-string v2, \"INAPP_V3\"",
              ".line 9",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 10",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$j;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto/16 :goto_1",
              ":sswitch_3",
              "const-string v2, \"ATTRIBUTE_CACHE\"",
              ".line 11",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 12",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$a;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto/16 :goto_1",
              ":sswitch_4",
              "const-string v2, \"DEVICE_TRIGGERS\"",
              ".line 13",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 14",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$d;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto/16 :goto_1",
              ":sswitch_5",
              "const-string v2, \"BATCH_DATA\"",
              ".line 15",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 16",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$b;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto/16 :goto_1",
              ":sswitch_6",
              "const-string v2, \"CAMPAIGNLIST\"",
              ".line 17",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 18",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$m;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto/16 :goto_1",
              ":sswitch_7",
              "const-string v2, \"USERATTRIBUTES\"",
              ".line 19",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 20",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$m;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto :goto_1",
              ":sswitch_8",
              "const-string v2, \"INAPPMSG\"",
              ".line 21",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 22",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$h;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto :goto_1",
              ":sswitch_9",
              "const-string v2, \"DATAPOINTS\"",
              ".line 23",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 24",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$f;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto :goto_1",
              ":sswitch_a",
              "const-string v2, \"MESSAGES\"",
              ".line 25",
              "invoke-virtual {v1, v2, v0, p2}, Landroid/database/sqlite/SQLiteDatabase;->insert(Ljava/lang/String;Ljava/lang/String;Landroid/content/ContentValues;J",
              "move-result-wide v1",
              "cmp-long p2, v1, v3",
              "if-lez p2, :cond_1",
              ".line 26",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moe/pushlibrary/providers/a$l;->a(Landroid/content/Context;)Landroid/net/Uri;",
              "move-result-object p2",
              "invoke-static {p2, v1, v2}, Landroid/content/ContentUris;->withAppendedId(Landroid/net/Uri;J)Landroid/net/Uri;",
              "move-result-object p2",
              "goto :goto_1",
              ".line 27",
              ":goto_0",
              "invoke-direct {p2}, Ljava/lang/StringBuilder;-><init>()V",
              "const-string v1, \"Unknown URI \"",
              "invoke-virtual {p2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
              "invoke-virtual {p2, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;",
              "invoke-virtual {p2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;",
              "move-result-object p2",
              "invoke-static {p2}, Lcom/moengage/core/i;->b(Ljava/lang/String;)V",
              ":try_end_0",
              ".catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_1",
              ":cond_1",
              "move-object p2, v0",
              ":goto_1",
              "if-eqz p2, :cond_2",
              ".line 28",
              ":try_start_1",
              "new-instance v1, Ljava/lang/StringBuilder;",
              "invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V",
              "const-string v2, \"MoEProvider: Added new record : \"",
              "invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
              "invoke-virtual {p2}, Landroid/net/Uri;->toString()Ljava/lang/String;",
              "move-result-object v2",
              "invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
              "invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;",
              "move-result-object v1",
              "invoke-static {v1}, Lcom/moengage/core/i;->e(Ljava/lang/String;)V",
              ".line 29",
              "invoke-virtual {p0}, Landroid/content/ContentProvider;->getContext()Landroid/content/Context;",
              "move-result-object v1",
              "invoke-virtual {v1}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;",
              "move-result-object v1",
              "invoke-virtual {v1, p1, v0}, Landroid/content/ContentResolver;->notifyChange(Landroid/net/Uri;Landroid/database/ContentObserver;V",
              "goto :goto_3",
              ".line 30",
              ":cond_2",
              "new-instance v0, Ljava/lang/StringBuilder;",
              "invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V",
              "const-string v1, \"MoEProvider: Failed to add new record: \"",
              "invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
              "invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;",
              "invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;",
              "move-result-object p1",
              "invoke-static {p1}, Lcom/moengage/core/i;->b(Ljava/lang/String;)V",
              ":try_end_1",
              ".catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0",
              "goto :goto_3",
              ":catch_0",
              "move-exception p1",
              "move-object v0, p2",
              "goto :goto_2",
              ":catch_1",
              "move-exception p1",
              ":goto_2",
              "const-string p2, \"MoEProvider insert() : \"",
              ".line 31",
              "invoke-static {p2, p1}, Lcom/moengage/core/i;->c(Ljava/lang/String;Ljava/lang/Throwable;)V",
              "move-object p2, v0",
              ":goto_3",
              "return-object p2",
              "nop",
              ":sswitch_data_0",
              ".sparse-switch",
              "0x1 -> :sswitch_a",
              "0x3 -> :sswitch_9",
              "0x5 -> :sswitch_8",
              "0x9 -> :sswitch_7",
              "0xb -> :sswitch_6",
              "0xd -> :sswitch_5",
              "0xf -> :sswitch_4",
              "0x11 -> :sswitch_3",
              "0x13 -> :sswitch_2",
              "0x15 -> :sswitch_1",
              "0x17 -> :sswitch_0",
              ".end sparse-switch"]
    checker = SqlInjectionChecker()
    checker.check_insert(method)


run()
