library("TAM")

D1 <- read.csv("item_matrix.csv")
anchor <- read.csv("item_difficulties.csv")
anchor
mod1 <- tam(D1, xsi.fixed=anchor, control = list(maxiter = 100))

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
