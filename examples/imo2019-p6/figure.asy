settings.outformat = "pdf";
size(18cm);
defaultpen(fontsize(16pt));
import olympiad;

pair A = (-0.256, 0.966);
pair B = (-0.905, -0.426);
pair C = (0.943, -0.333);
pair I = (-0.12130476210410489, 0.10145912502691619);
pair D = (-0.09680735970648323, -0.38532796777743666);
pair E = (0.236851296097036, 0.4320435082318184);
pair F = (-0.5630541866027495, 0.3074184472249194);
pair R = (-0.24605643069891492, 0.5726266298783805);
pair P = (-0.2220922695192179, -0.37540948873813806);
pair Q = (-0.20285179361470118, 0.08561949612402289);
path __obj434 = (-0.905, -0.426) -- (0.943, -0.333);
path __obj437 = (-0.256, 0.966) -- (0.943, -0.333);
path __obj440 = (-0.905, -0.426) -- (-0.256, 0.966);
path __obj443 = (-0.5630541866027495, 0.3074184472249194) -- (0.236851296097036, 0.4320435082318184);
path __obj444 = (-0.24605643069891492, 0.5726266298783805) -- (-0.09680735970648323, -0.38532796777743666);
path __obj447 = (-0.256, 0.966) -- (-0.2220922695192179, -0.37540948873813806);
path __obj959 = (-0.12130476210410489, 0.10145912502691619) -- (-0.09680735970648323, -0.38532796777743666);
path __obj960 = (-0.2220922695192179, -0.37540948873813806) -- (-0.20285179361470118, 0.08561949612402289);
path __obj961 = (-0.256, 0.966) -- (-0.256, 0.966);
path omega = circle((-0.12130476210410489, 0.10145912502691619), 0.4874031149317212);
path __obj696 = circle((0.35369503921765627, -0.16852328051704166), 0.6118275312982862);
path __obj949 = circle((-0.5836443317711653, -0.12940457827913934), 0.4373080260966816);

dot('$A$', A, dir(90));
dot('$B$', B, dir(90));
dot('$C$', C, dir(90));
dot('$I$', I, dir(90));
dot('$D$', D, dir(90));
dot('$E$', E, dir(90));
dot('$F$', F, dir(90));
dot('$R$', R, dir(90));
dot('$P$', P, dir(90));
dot('$Q$', Q, dir(90));
draw(__obj434);
draw(__obj437);
draw(__obj440);
draw(__obj443);
draw(__obj444);
draw(__obj447);
draw(__obj959);
draw(__obj960);
draw(__obj961);
draw(omega);
draw(__obj696);
draw(__obj949);

