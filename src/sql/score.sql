
CREATE FUNCTION iris_score(varchar(1356), float, float, float, float) \
returns float LANGUAGE PYTHON  parameter style \
NPSGENERIC  FENCED  NOT THREADSAFE  NO FINAL CALL  ALLOW PARALLEL  NO DBINFO  DETERMINISTIC  NO EXTERNAL ACTION \
RETURNS NULL ON NULL INPUT  NO SQL \
external name '/database/config/db2inst1/sqllib/function/routine/score.py'



with input (model, sepal_length, sepal_width, petal_length, petal_width) as
(select varchar(models.model), iris.sepal_length, iris.sepal_width, iris.petal_length, iris.petal_width
from models, iris
where models.id =1)
select iris_score(varchar(model), float(sepal_length), float(sepal_width), float(petal_length), float(petal_width) ) from input