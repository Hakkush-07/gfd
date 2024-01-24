# Figures of Geometry Problems

### Syntax of gfd (Geometric Figure Description) files

#### Possible Lines

`<variables>` = `<expression>`

\> `<param count>` `<function id>` = `<function body>`

% `<import file>`

\# `<comments>`

#### Explanations

`<expression>`: mix of `<variable>`, `<function>`, uses postfix

`<function body>`: mix of `$<parameter index>`, `<variable>`, `<function>`, again postfix

`<function>` can include trailing * which means that output of that function will be included with a random label in the final figure (used for including the outputs of inline calls)

when an import line encountered, execution switches to that file

parameters are passed to the functions in reverse of the stack order, first popped element becomes last argument (because that is more intuitive, I guess)

### Run

```sh
python main.py examples/imo2012-p1/figure
```

```sh
asy examples/imo2012-p1/figure.asy -o examples/imo2012-p1/figure.pdf
```