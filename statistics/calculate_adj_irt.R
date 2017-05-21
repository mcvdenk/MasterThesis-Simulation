library("TAM")

D1 <- read.csv("item_matrix.csv", row.names = 1)
items = colnames(D1)
cls <- c(V1="integer", V2="numeric")
anchor_df <- read.csv("item_difficulties.csv", colClasses=cls, stringsAsFactors=FALSE, header=FALSE)
str(anchor_df)
anchor <- as.matrix(anchor_df)
str(anchor)

mod1 <- tam(D1, xsi.fixed=anchor_df, control = list(maxiter = 300))
#mod1 <- tam(D1, xsi.fixed=anchor_df)

ItemDiff <- mod1$item
write.csv(ItemDiff, file='ItemDiff.csv')

Abil <- mod1$person
write.csv(Abil, file='Abil.csv')

Rel <- mod1$EAP.rel
write.csv(Rel, file='Rel.csv')

#hist(ItemDiff)
#hist(PersonAbility)
#mean(ItemDiff)
#mean(PersonAbility)
#sd(ItemDiff)
#sd(PersonAbility)
