# Coding rules (from the my-setup plugin)

- Before writing a helper, search the repo for an existing one and reuse it.
- Don't copy a block of logic. Extract it once it appears a second time.
- Don't add an interface, base class or factory that has only one implementation or one caller.
- Keep a function to one job. If you need "and" to describe it, split it.
- Follow the patterns already in the file and module, even where you would design it differently.
