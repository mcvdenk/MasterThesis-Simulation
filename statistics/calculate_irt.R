library("TAM")

D1 <- read.csv("item_matrix.csv", row.names = 1)

#mod1 <- tam(D1, control = list(maxiter = 10))
mod1 <- tam(D1, control = list(maxiter = 300))
#mod1 <- tam(D1)

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
