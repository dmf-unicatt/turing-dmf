# Turing @ DMF: local patches for compatibility with mathrace in-house implementation

This directory contains a few local patches. Most of them are related to changes required to make **Turing** behave as **mathrace**:

0. `0000_customize_footer.patch`: customize the footer of the website, to acknowledge that customizations were carried out.
1. `0001_show_elapsed_time_instead_of_countdown.patch`: this change affects how time is displayed in all classification views. **Turing** displays a countdown to the end of the race, while **mathrace** displays the elapsed time since the beginning of the race. To ease comparison with **mathrace**, **Turing @ DMF** has patched **Turing** to display the elapsed time instead of a countdown.
2. `0002_change_elapsed_time_via_textbox.patch`: this change affects how time is displayed in all classification views of races which have already ended. A text box was added to manually write the value of the elapsed time, and ease the visual comparison of intermediate states between **Turing**/**Turing @ DMF** and **mathrace**.
3. `0003_penalize_wrong_answer_after_correct_answer.patch`: this change affects the score of a team which submits an incorrect answer after having already provided a correct answer to the same question. In that case, **Turing** does not penalize the team by deducting 10 points out of their current score, while **mathrace** does reduce their score by 10 points. To preserve compatibility with **mathrace**, in that case **Turing @ DMF** penalizes the team.
4. `0004_selenium_updates.patch`: update internal tests to support new `selenium` versions.
5. `0005_serve_static_files_with_whitenoise.patch`: use [`whitenoise`](https://pypi.org/project/whitenoise/) to serve static files.
6. `0006_test_pk_for_postgres.patch`: update tests for compatibility with PostgreSQL. It seems that SQLite3 uses a standalone database at every test and/or resets primary keys at every test, while PostgreSQL does not. Due to this, some hardcoded primary keys had to be replaced with a value fetched from the current database state.
7. `0007_durata_blocco.patch`: allow customization of the deadline time for question score periodic increase.
8. `0008_default_n_k_blocco.patch`: add default values for `n_blocco` and `k_blocco`. **mathrace** only supports the case `k_blocco = 1`, and therefore we prefer to provide this value as the default to facilitate setting up **mathrace**-compatible races in **Turing @ DMF**.
9. `0009_upload_journal.patch`: allow user to upload and import a **mathrace** journal.
10. `0010_update_requirements.patch`: update versions in `requirements.txt`, after checking that tests still run correctly.
11. `0011_models_to_from_dict_fixes.patch`: fixes to `Gara.create_from_dictionary` and `Gara.to_dict`, so that the latter returns a fully serialized object, and the former does not change the input dictionary.
