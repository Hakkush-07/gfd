settings.outformat = "pdf";
size(18cm);
defaultpen(fontsize(16pt));
import olympiad;

pair A = (-0.256, 0.966);
pair B = (-0.905, -0.426);
pair C = (0.943, -0.333);
pair J = (-0.12130476210410489, 0.10145912502691619);
pair M = (-0.09680735970648323, -0.38532796777743666);
pair K = (-0.5630541866027495, 0.3074184472249194);
pair L = (0.236851296097036, 0.4320435082318184);
pair F = (0.18645927103096666, 0.30859697630188304);
pair G = (-0.5392666307374498, 0.2720750559206802);
pair S = (0.6289185420619332, -0.34880604739623394);
pair T = (-0.8225332614748995, -0.42184988815863944);
path u = (-0.905, -0.426) -- (0.943, -0.333);
path v = (-0.256, 0.966) -- (0.943, -0.333);
path w = (-0.905, -0.426) -- (-0.256, 0.966);
path __obj157 = (-0.09680735970648323, -0.38532796777743666) -- (0.236851296097036, 0.4320435082318184);
path __obj158 = (-0.905, -0.426) -- (0.18645927103096666, 0.30859697630188304);
path __obj160 = (-0.5630541866027495, 0.3074184472249194) -- (-0.09680735970648323, -0.38532796777743666);
path __obj161 = (-0.5392666307374498, 0.2720750559206802) -- (0.943, -0.333);
path __obj163 = (-0.256, 0.966) -- (0.6289185420619332, -0.34880604739623394);
path __obj165 = (-0.8225332614748995, -0.42184988815863944) -- (-0.256, 0.966);

dot('$A$', A, dir(90));
dot('$B$', B, dir(90));
dot('$C$', C, dir(90));
dot('$J$', J, dir(90));
dot('$M$', M, dir(90));
dot('$K$', K, dir(90));
dot('$L$', L, dir(90));
dot('$F$', F, dir(90));
dot('$G$', G, dir(90));
dot('$S$', S, dir(90));
dot('$T$', T, dir(90));
draw(u);
draw(v);
draw(w);
draw(__obj157);
draw(__obj158);
draw(__obj160);
draw(__obj161);
draw(__obj163);
draw(__obj165);
