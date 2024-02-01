# GFD File Syntax

## Possible Lines

`<variables>` = `<expression>`

\> `<param count>` `<function id>` = `<function body>`

% `<import file>`

\# `<comments>`

? `<check expression>`

## Explanations

`<expression>`: mix of `<variable>`, `<function>`, uses postfix

`<check expression>`: mix of `<variable>`, `<check function>`, uses postfix

`<function body>`: mix of `$<parameter index>`, `<variable>`, `<function>`, again postfix

`<function>` can include trailing * which means that output of that function will be included with a random label in the final figure (used for including the outputs of inline calls)

when an import line encountered, execution switches to that file

parameters are passed to the functions in reverse of the stack order, first popped element becomes last argument (because that is more intuitive, I guess)
