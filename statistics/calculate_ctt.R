library("CTT")

D1 <- read.csv("item_matrix.csv", row.names = 1)

mod1 <- reliability(D1, itemal = TRUE, NA.Delete = FALSE)
alpha <- mod1$alpha
write.csv(alpha, file='Rel.csv')
max_alpha = mod1$alphaIfDeleted
write.csv(max_alpha, file='MaxRel.csv')
