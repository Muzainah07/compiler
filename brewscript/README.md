# BrewScript Compiler Project

## Introduction

BrewScript is a small programming language developed for our Compiler Construction project. In this project, we are working on a lexical analyzer and a parser.

The lexical analyzer reads the source code and converts it into tokens. After that, the parser checks whether the tokens follow the grammar rules of BrewScript.

## Project Files

- `brewscript_lexer.py` – Reads the source code and generates tokens.
- `recursive_descent_parser.py` – Checks the tokens according to the CFG.
- `main.py` – Runs the lexical analyzer and parser.
- `valid_test.brew` – Used to test a valid program.
- `syntax_error_test.brew` – Used to test a program with a syntax error.
- `lexical_errors.brew` – Used to test lexical errors.

Keep these files in the same project folder.

## How to Run the Project

1. Open the project folder in a terminal.
2. Run the following command:

   ```bash
   python main.py
   ```

3. Enter the name of the `.brew` file when asked.
4. Check the output to see the tokens and parsing result.


## Context-Free Grammar (CFG)

The following grammar rules are used by the parser:

```text
<Program>         → #roast <Program'>
<Program'>        → <Block> #brew_end
                  | <StmtList> #brew_end
<Block>           → { <StmtList> }
<StmtList>        → <Stmt> <StmtList> | ε
<Stmt>            → <MatchedStmt> | <UnmatchedStmt>
<MatchedStmt>     → profile <Expr> ? <MatchedStmt> adjust ? <MatchedStmt>
                  | infuse <Expr> : <MatchedStmt>
                  | <VarDecl> ;
                  | <Assignment> ;
                  | <OutputStmt> ;
                  | <Block>
<UnmatchedStmt>   → profile <Expr> ? <UnmatchedStmt'>
                  | infuse <Expr> : <UnmatchedStmt>
<UnmatchedStmt'>  → <Stmt>
                  | <MatchedStmt> adjust ? <UnmatchedStmt>
<VarDecl>         → DT <IdList>
<IdList>          → ID <IdList'>
<IdList'>         → , <IdList> | ε
<Assignment>      → ID <Assignment'>
<Assignment'>     → <AssignOp> <Expr>
                  | = <InputExpr>
                  | ++
                  | --
<AssignOp>        → = | +=
<OutputStmt>      → pull ( <ArgList> )
<ArgList>         → <Expr> <ArgList'>
<ArgList'>        → , <ArgList> | ε
<InputExpr>       → barista ( <InputExpr'>
<InputExpr'>      → TEXT_LITERAL )
                  | )
<Expr>            → <LogOrExpr>
<LogOrExpr>       → <LogAndExpr> <LogOrExpr'>
<LogOrExpr'>      → || <LogAndExpr> <LogOrExpr'> | ε
<LogAndExpr>      → <RelExpr> <LogAndExpr'>
<LogAndExpr'>     → && <RelExpr> <LogAndExpr'> | ε
<RelExpr>         → <AddExpr> <RelExpr'>
<RelExpr'>        → <RelOp> <AddExpr> | ε
<RelOp>           → < | <= | > | >= | == | !=
<AddExpr>         → <MulExpr> <AddExpr'>
<AddExpr'>        → + <MulExpr> <AddExpr'> | - <MulExpr> <AddExpr'> | ε
<MulExpr>         → <UnaryExpr> <MulExpr'>
<MulExpr'>        → x <UnaryExpr> <MulExpr'> | / <UnaryExpr> <MulExpr'> | % <UnaryExpr> <MulExpr'> | ε
<UnaryExpr>       → ! <UnaryExpr> | - <UnaryExpr> | + <UnaryExpr> | <Factor>
<Factor>          → ( <Expr> ) | ID | INT_LITERAL | TEXT_LITERAL
```

## Conclusion

This project helps us understand how a compiler checks source code. The lexical analyzer identifies tokens and reports lexical errors, while the parser checks whether the program follows the defined CFG.

The three test cases are used to check successful parsing, syntax errors, and lexical errors.
