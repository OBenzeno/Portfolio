library("ggplot2")
library("palmerpenguins")

ggplot(data=penguins)+
  geom_point(mapping=aes(x=flipper_length_mm,y=body_mass_g,shape=species,color=species))

ggplot(data=penguins)+
  geom_point(mapping=aes(x=bill_length_mm,y=bill_depth_mm,shape=species,color=species))

data(penguins)
View(penguins)

ggplot(data=penguins)+
  geom_smooth(mapping=aes(x=flipper_length_mm,y=body_mass_g))+
  geom_point(mapping=aes(x=flipper_length_mm,y=body_mass_g,shape=species,color=species))

ggplot(data=penguins,aes(x=flipper_length_mm,y=body_mass_g))+
  geom_point(aes(shape=species,color=species))+
  facet_wrap(~species)

ggplot(data=penguins,aes(x=flipper_length_mm,y=body_mass_g))+
  geom_point(aes(color=species))+
  facet_wrap(~species)

ggplot(data=penguins)+
  geom_point(mapping=aes(x=flipper_length_mm,y=body_mass_g,shape=species,color=species))+
  facet_grid(sex~species)

ggplot(data=penguins)+
  geom_point(mapping=aes(x=flipper_length_mm,y=body_mass_g,shape=species,color=species))+
  facet_grid(~sex)

ggplot(data=penguins)+
  geom_smooth(mapping=aes(x=flipper_length_mm,y=body_mass_g))+
  geom_point(mapping=aes(x=flipper_length_mm,y=body_mass_g,shape=species,color=species))+
  labs(title="Palmer Penguins: Body Mass vs Flipper Length",subtitle="Sample of Three Penguin Species",
    caption="Data collected by Dr. Kristen Gorman")+
  annotate("text", x=220,y=3500, label="The Gentoos are the largest", color="Purple",
    fontface="bold", size=3.5, angle=25)

p <- ggplot(data=penguins)+
  geom_smooth(mapping=aes(x=flipper_length_mm,y=body_mass_g))+
  geom_point(mapping=aes(x=flipper_length_mm,y=body_mass_g,shape=species,color=species))+
  labs(title="Palmer Penguins: Body Mass vs Flipper Length",
       caption="Data collected by Dr. Kristen Gorman")

p+annotate("text", x=220,y=3500, label="The Gentoos are the largest")
