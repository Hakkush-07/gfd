settings.outformat = "pdf";
size(18cm);
defaultpen(fontsize(16pt));
import olympiad;

pair A = (-0.256, 0.966);
pair B = (-0.905, -0.426);
pair C = (0.943, -0.333);
pair O = (-6.708819339037093e-05, -0.0006185055765011766);
pair P = (0.2558658236132192, -0.967237011153002);
path u = A -- P;
path t = circle((-6.708819339037093e-05, -0.0006185055765011766), 0.9999264926327126);
path t = circle((-6.708819339037093e-05, -0.0006185055765011766), 0.9999264926327126);

dot("$A$", A, dir(104.82998670601133));
dot("$B$", B, dir(205.17679291089772));
dot("$C$", C, dir(340.5851292100229));
dot("$O$", O, dir(194.8299867060113));
dot("$P$", P, dir(284.8299867060113));
draw(u);
draw(t);
draw(t);

