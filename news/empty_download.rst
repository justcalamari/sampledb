**Added:** None

**Changed:**

* Print message when attempting to download an empty spreadsheet instead of raising an error.

**Deprecated:** None

**Removed:** None

**Fixed:** None

**Security:**

* Use try/except/finally to make sure ssh tunnels are closed if there is an exception.
