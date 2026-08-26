Attack #1: Add a note with an empty body

Result:
The CLI accepted the note and saved it with an empty body.

Expected:
An empty note body should be rejected.

Status:
Potential bug — needs further confirmation.

Attack #2: 100,000-character note

Attempt:
Generated a 100,000-character body and passed it to the CLI.

Result:
The shell returned "Argument list too long".

Observation:
The input did not reach the application, so this attack did not test the application's size limit.


*Attack #2: Add a note with 100,000 characters

Result:
The application accepted the 100,000-character note.

Observation:
There appears to be no size-limit validation preventing a very large note body.

Attack #3: Emoji and Bengali text

Result:
The application successfully stored and displayed Bengali text and emoji.

Observation:
No encoding problem was found.

Status:
Passed — no issue observed.

Attack #4: Delete a note that does not exist

Result:
The command completed silently without an error or message.

Observation:
Deleting a nonexistent note is silently ignored.

Status:
Potential issue — error handling should be reviewed.

Attack #5: Search with regex special character .*

Result:
The command completed without an error or output.

Observation:
No crash occurred, but the search behavior with this special character needs review.

Attack #6: Corrupt JSON file

Result:
Running the list command with a corrupted notes.json caused
the application to crash with JSONDecodeError and display
a full traceback.

Expected:
The application should fail gracefully when the JSON file
is invalid.

Status:
Bug found — graceful error handling is missing.

Attack #7: Read-only JSON file

Result:
Adding a note to a read-only notes.json caused the application
to crash with an unhandled PermissionError and full traceback.

Expected:
The application should handle the permission error gracefully.

Status:
Bug found — permission error handling is missing.

Attack #8: Two simultaneous adds

Result:
Both commands completed successfully, and both notes were saved.

Observation:
No data loss or JSON corruption was observed; both notes were present in the file after the simultaneous adds.




Based on the documented results, the bugs or potential issues are:

Attack #1: Empty note body is accepted.
Attack #2: 100,000-character note is accepted.
Attack #4: Deleting a nonexistent note gives no message.
Attack #6: Corrupt JSON causes an unhandled JSONDecodeError.
Attack #7: Read-only file causes an unhandled PermissionError.

I think #1,#6 and #7 are the most potential Issue 