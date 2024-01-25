settings.outformat = "pdf";
size(18cm);
defaultpen(fontsize(16pt));
import olympiad;

dot('$A$', (-0.256, 0.966), dir(90));
dot('$B$', (-0.905, -0.426), dir(90));
dot('$C$', (0.943, -0.333), dir(90));
draw((-0.905, -0.426) -- (0.943, -0.333));
draw((-0.256, 0.966) -- (0.943, -0.333));
draw((-0.905, -0.426) -- (-0.256, 0.966));
draw(circle((-6.708819339037093e-05, -0.0006185055765011766), 0.9999264926327126));
dot('$S$', (-0.05032446429058158, 0.9980441936451045), dir(90));
draw((-0.905, -0.426) -- (-0.05032446429058158, 0.9980441936451045));
dot('$D$', (-0.24157615531554943, 0.6793842475605947), dir(90));
dot('$E$', (-0.15766318271404786, -0.9880477241337589), dir(90));
draw((-2.241002150452671, 0.5787637835196032) -- (-0.15766318271404786, -0.9880477241337589));
dot('$L$', (-2.241002150452671, 0.5787637835196032), dir(90));
draw(circle((-1.2360239603522638, 0.5244495445847032), 1.0064448316368695));
dot('$P$', (-0.32212735504853585, 0.9460230185401785), dir(90));
draw((-0.32212735504853585, 0.9460230185401785) -- (-0.32212735504853524, 0.9460230185401789));
draw((-0.21757564754973124, 0.719373439131497) -- (-0.21757564754973124, 0.719373439131497));
dot('$T$', (-0.21757564754973124, 0.719373439131497), dir(90));
// concurrent(x, y, z) = True

