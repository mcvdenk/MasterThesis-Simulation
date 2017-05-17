library("CTT")

D1 <- read.csv("item_matrix.csv")

mod1 <- reliability(D1, NA.Delete = FALSE)
alpha <- mod1$alpha
alpha
