library("TAM")

D1 <- read.csv("test_data.csv")

mod1 <- tam(D1[, ! colnames(D1) %in% c('i2')])
mod1$xsi
ItemDiff <- mod1$xsi$xsi
ItemDiff

Abil <- tam.wle(mod1)
Abil
PersonAbility <- Abil$theta
PersonAbility

hist(ItemDiff)
hist(PersonAbility)
mean(ItemDiff)
mean(PersonAbility)
sd(ItemDiff)
sd(PersonAbility)
