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

## Functions

In all functions, parameter names indicate the type

| Parameter Name   | Parameter Type |
| ---------------- | -------------- |
| a, b, c, d, ...  | Point          |
| u, v, w, x, y, z | Line           |
| s, t, m          | Circle         |

### Construction Functions

Functions that take objects from the figure and produce objects

| Name  | Parameters | Returns | Description | Preconditions |
| ---- | ---- | ---- | ---- | ---- |
|triangle|-|P, P, P|predefined triangle|-|
|unit_circle|-|C|unit circle|-|
|random_point_on_circle|s|P|random point on circle s|-|
|random_point_on_unit_circle|-|P|random point on unit circle|-|
|random_point_on_segment|a, b|P|random point on the line segment ab|-|
|random_point_on_arc|s, a, b|P|random point on the arc ab of circle s|a and b to be on s|
|random_point|-|P|random point on unit circle|-|
|random_line|-|L|random line passing through two random points on the unit circle|-|
|random_circle|-|C|random circle whose center is on the unit circle and has a radius between 0 and 1|-|
|random_triangle_on_circle|s|P, P, P|random triangle on circle s|-|
|random_triangle_on_unit_circle|-|P, P, P|random triangle on unit circle|-|
|random_nice_triangle|-|P, P, P|random nice triangle, angles close to 60, 45, 75|-|
|random_line_through_point|a|L|random line through point a|-|
|center|s|P|center of s|-|
|midpoint|a, b|P|midpoint of ab|-|
|line|a, b|L|line ab|-|
|perpendicular_bisector|a, b|L|perpendicular bisector of ab|-|
|circle_diameter|a, b|C|circle with diameter ab|-|
|reflection_pp|a, b|P|reflection of a over b|-|
|perpendicular_through|a, b|L|line through a perpendicular to ab|-|
|circle_centered|a, b|C|circle centered a through b|-|
|reflection_pl|a, u|P|reflection of a over u|-|
|foot|a, u|P|foot of a on u|-|
|perpendicular_line|a, u|L|line through a perpendicular to u|-|
|parallel_line|a, u|L|line through a parallel to u|-|
|tangent_points|a, s|P, P|touch points of tangents from a to s|a to be outside of s|
|tangent_lines|a, s|L, L|tangent lines from a to s|a to be outside of s|
|tangent_line|a, s|L|line through a tangent to s|a to be on s|
|polar|a, s|L|polar line of a wrt s|a to not be center of s|
|intersection_ll|u, v|P|intersection of u and v|u and v to not be parallel|
|angle_bisector|u, v|L|angle bisector of u and v|-|
|angle_bisector2|u, v|L|angle bisector of u and v, other|-|
|reflection_ll|u, v|L|reflection of u over v|u and v to not be parallel|
|intersections_lc|u, s|P, P|intersection points of u and s|u and s to intersect|
|intersection_lc|u, s|P|tangent point of u and s|u and s to be tangent|
|tangent_point|u, s|P|tangent point of u and s|u and s to be tangent|
|pole|u, s|P|pole point of u wrt s|u to not pas through center of s|
|intersections_cc|s, t|P, P|intersection points of s and t|s and t to intersect|
|intersection_cc|s, t|P|tangent point of s and t|s and t to be tangent|
|radical_axis|s, t|L|radical axis of s and t|-|
|tangent_points_external|s, t|P, P, P, P|external tangent points of s and t|...|
|tangent_points_internal|s, t|P, P, P, P|internal tangent points of s and t|...|
|tangent_intersection_external|s, t|P|intersection of external tangents of s and t|...|
|tangent_intersection_internal|s, t|P|intersection of internal tangents of s and t|...|
|tangent_lines_external|s, t|L, L|external tangents of s and t|...|
|tangent_lines_internal|s, t|L, L|internal tangents of s and t|...|
|internal_angle_bisector|a, b, c|-|internal angle bisector of angle bac|-|
|external_angle_bisector|a, b, c|L|external angle bisector of angle bac|-|
|altitude|a, b, c|L|altitude from a to bc|-|
|median|a, b, c|L|median from a to bc|-|
|foot_ppp|a, b, c|P|foot from a to bc|-|
|circumcenter|a, b, c|P|circumcenter of abc|-|
|circumcircle|a, b, c|C|circumcircle of abc|-|
|incenter|a, b, c|P|incenter of abc|-|
|incircle|a, b, c|C|incircle of abc|-|
|excenter|a, b, c|P|a-excenter of abc|-|
|excircle|a, b, c|C|a-excircle of abc|-|
|orthocenter|a, b, c|P|orthocenter of abc|-|
|centroid|a, b, c|P|centroid of abc|-|
|second_intersection_plc|a, u, s|P|intersection of u and s other than a|a to be on u and s, requires u and s to intersect|
|second_intersection_pcc|a, s, t|P|intersection of s and t other than a|a to be on s and t, requires s and t to intersect|
|midpoint_of_arc|a, b, s|P|midpoint of arc ab of circle s|a and b to be on s|

### Check Functions

Functions that take objects from the figure and give boolean result.

| Name | Parameters | Description |
| ---- | ---------- | ----------- |
|is_collinear|a, b, c|a, b, c are collinear|
|is_concyclic|a, b, c, d|a, b, c, d are concyclic|
|is_concurrent|u, v, w|u, v, w are concurrent|
|is_parallel|u, v|u and v are parallel|
|is_perpendicular|u, v|u and v are perpendicular|
|is_tangent|s, t|s and t are tangent|
|is_pl|a, u|a is on u|
|is_pc|a, s|a is on s|
|is_lc|u, s|u is tangent to s|
