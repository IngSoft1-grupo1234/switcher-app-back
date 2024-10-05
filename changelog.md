
---
## CHANGELOG 

1> Se acuerdan del error de cambiar `query().get` a `get( , )`? Bueno, para reparar los test con eso había que cambiar todos los `query.get` de los test a solo `.get`, y después los `assert_any_call` comen los Model.

2> Des-chanchie un poco algunos `match_router` al poner los `HTTPException` en los `match_crud`. Esto hace que los crud no tengan que enviar los strings y que los routers no tengan que checkear 4 strings, viste. Creo que me faltan funciones para cambiar esto. Esto hace que cambie todo el test y tarde un buen tiempo en arreglarlo.

3> Hice una función simple `broadcast_to_id_list` para hacer un broadcast a los jugadores de una partida, le pasas una lista con los ids y ya.

4> Al crear una partida se une automaticamente el host. Nunca mas ese 0/4 en una demo.

5> Bue lo de los turnos. Es una lista convertida a string dentro de MatchModel. Los test de get estan funcionando magicamente. (chequear)

6> No tengo idea que mas hice. Funca igual xd.

### TODO

- Hay que cambiar los router test para que sean parecidos a los crud test.
- Hay que hacer una forma de testear más rápido sin usar el Swagger UI de FastAPI (SCRUM-74).
- Modularizar los get_matches?

---
