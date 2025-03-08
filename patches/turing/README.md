# Turing @ DMF: local patches for compatibility with mathrace in-house implementation

This directory contains some local patches. A few of them are related to changes required to make **Turing** behave as **mathrace**:

0. `0000_customize_footer.patch`: customize the footer of the website, to acknowledge that customizations were carried out.
1. `0001_show_elapsed_time_instead_of_countdown.patch`: this change affects how time is displayed in all classification views. **Turing** displays a countdown to the end of the race, while **mathrace** displays the elapsed time since the beginning of the race. To ease comparison with **mathrace**, **Turing @ DMF** has patched **Turing** to display the elapsed time instead of a countdown.
2. `0002_change_elapsed_time_via_textbox.patch`: this change affects how time is displayed in all classification views of races which have already ended. A text box was added to manually write the value of the elapsed time, and ease the visual comparison of intermediate states between **Turing**/**Turing @ DMF** and **mathrace**.
3. `0003_penalize_wrong_answer_after_correct_answer.patch`: this change affects the score of a team which submits an incorrect answer after having already provided a correct answer to the same question. In that case, **Turing** does not penalize the team by deducting 10 points out of their current score, while **mathrace** does reduce their score by 10 points. To preserve compatibility with **mathrace**, in that case **Turing @ DMF** penalizes the team.
4. `0004_selenium_updates.patch`: update internal tests to support new `selenium` versions.
5. `0005_serve_static_files_with_whitenoise.patch`: use [`whitenoise`](https://pypi.org/project/whitenoise/) to serve static files.
6. `0006_test_pk_for_postgres.patch`: update tests for compatibility with PostgreSQL. It seems that SQLite3 uses a standalone database at every test and/or resets primary keys at every test, while PostgreSQL does not. Due to this, some hardcoded primary keys had to be replaced with a value fetched from the current database state.
7. `0007_generalize_race_parameters.patch`: allow customization of the deadline time for question score periodic increase. Furthermore, isolate the remaining the race parameters in the javascript client, so that they can be generalized more easily in the django interface in future.
8. `0008_default_n_k_blocco.patch`: add default values for `n_blocco` and `k_blocco`. **mathrace** only supports the case `k_blocco = 1`, and therefore we prefer to provide this value as the default to facilitate setting up **mathrace**-compatible races in **Turing @ DMF**.
9. `0009_upload_journal.patch`: allow user to upload and import a **mathrace** journal. Furthermore, be explicit in allowing or disallowing race events that will end up being in the future.
10. `0010_update_requirements.patch`: update versions in `requirements.txt`, after checking that tests still run correctly.
11. `0011_models_to_from_dict_fixes.patch`: fixes to `Gara.create_from_dictionary` and `Gara.to_dict`, so that the latter returns a fully serialized object, and the former does not change the input dictionary.
12. `0012_events_str_local_time_zone.patch`: change `str` representation of race events (`Evento` and `Jolly`) to ensure that the local time zone is respected, otherwise the representation of the date may be confusing to the administrator in the django admin webpage.
13. `0013_display_protocol_numbers.patch`: display the protocol number (primary key in the database) and the insertion date when adding a new answer or jolly selection through the web interface.
14. `0014_manual_bonus.patch`: add feature to assign (positive or negative) bonus to a team. As a side effect, for simplicity of the implementation of the new feature the commentary has been disabled.
15. `0015_classification_time_from_server_and_querystring.patch`: stop using `Date.now()` in the calculation of the classification and use the server datetime instead, since the browser date may not agree with the one on the server. Furthermore, allow the admin to pass to querystrings while viewing classifications: `t` view classifications at an arbitrary point in time, and `ended` to switch between the live update and the replay modes.
16. `0016_improve_admin_panel.patch`: improve admin panel by enabling filtering on relevant model fields.
17. `0017_clarify_insertion_form_error.patch`: clarify error message in insertion form, explaining where the error details are.
18. `0018_suspend_reset_delete_button.patch`: administrators will now find additional buttons on the home page to suspend a running race, reset any race, or delete any race.
19. `0019_users_and_upload_in_race_creation_edit.patch`: change race creation page to select admin user and introducer users, as well as upload the team names, question names and question answers from text file. The chosen admin/introducers can also be modified on the race edit page.
20. `0020_logging_datetime_ip.patch`: add date and IP address to the log file.
21. `0021_logout_django_5.patch`: log out needs to be carried out via a POST request since django 5.
22. `0022_drop_favicon.patch`: drop usage of favicon, since it does not seem to be served correctly.
23. `0023_new_classification_type_final_proclamation.patch`: add a new classification type, typically used for proclamation of the final results.
24. `0024_team_selection_insertion_form.patch`: set `size` larger than one to the team `select` HTML element in the insertion form. The teams will be displayed in a scrollable list, rather than a dropdown, allowing to select a team with a single click (instead of two clicks in a dropdown).
25. `0025_offset_star.patch`: in the unica classification, move the star representing the jolly to the bottom right of the cell, otherwise the text would be broken in two lines (score first, then a new line and the star) if the score is higher than 100.
26. `0026_unica_position_range.patch`: in the unica classification, allow to only display a subset of the classification based on a position range provided via a querystring.
