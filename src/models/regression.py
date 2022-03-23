


class Regression:
    def __init__(self, table_name, target, learn_rate, max_iter, features):
        self.table_name = table_name
        self.target = target
        self.learn_rate = learn_rate
        self.max_iter = max_iter
        self.features = features
        self.feature_names =  dict(zip(["m" + str(x) for x in range(0, len(features))], self.features))



    def equation(self):
        """parts of the query that derive the equation

        a.m1 -(sum((((train.sepal_length *a.b1)+a.intercept+(train.sepal_width*a.b2))-train.target)*train.sepal_length*train.sepal_width)/(select count from rates)) *(select learn_rate from rates)  as m1,
        """
        return "(" + "+".join(["(train.{feature}*a.{index})".format(feature= v, index = k) for k, v in self.feature_names.items()])  + "+a.intercept)"

    def error(self):
        return "(train.{target}-{equation})".format(target = self.target, equation = self.equation())
    def difference(self):
        return "({equation}-train.{target})".format(target = self.target, equation = self.equation())
    def betas(self):
        return ",\n".join(["a.{index} - (sum({difference}*train.{feature})/(select count from rates))*(select learn_rate from rates) as {index}".format(feature=v, index = k, difference=self.difference()) for k,v in self.feature_names.items()])
    def mse(self):
        return "AVG({error}*{error}) as MSE".format(error = self.error())
    def intercept(self):
        return "a.{index} - (sum({difference})/(select count from rates))*(select learn_rate from rates) as {index}".format(index = "c", difference = self.difference())
    def table(self):
        return "TABLE \n ( \n SELECT {query} \n FROM TRAINING AS TRAIN ) t".format(query = ",\n".join(["a.iteration", self.mse(), self.betas(), self.intercept()]))

    def train(self):
        return "TRAINING AS ( SELECT t.*, row_number() over() as row FROM {table_name} as t )".format(table_name=self.table_name)
    def rates(self):
        return "RATES (learn_rate, count) as (select {learn_rate} as learn_rate, (select count(*) from training) as count from sysibm.sysdummy1)".format(learn_rate = self.learn_rate)

    def learning(self):
        end = "\nUNION ALL SELECT a.iteration + 1, {betas},a.c, t.mse, {ms}, t.c FROM LEARNING A, \n {table} \n WHERE A.ITERATION<{max_iter} \n)".format(betas = ",".join( ["a.{x}".format(x =x) for x in self.feature_names.keys() ] ), ms =",".join( ["t.{x}".format(x =x) for x in self.feature_names.keys() ] ), table = self.table(), max_iter = self.max_iter )
        start = "LEARNING (iteration, {betas2}, intercept, mse, {betas}, c) as (select 1, {initial} FROM SYSIBM.SYSDUMMY1 {end} ".format(end = end, betas2 = ",".join(["b" + str(x) for x in range(0, len(self.features))]), betas = ",".join(self.feature_names.keys()), initial = ",".join(["CAST(0.0 as DOUBLE)" for x  in range(0, (len(self.features)*2)+3)]))
        return start

    def query(self):
        return "WITH \n" + ",\n".join([self.train(), self.rates(), self.learning()]) + "SELECT * FROM LEARNING \n order by MSE"








def main():

    regression = Regression(table_name="transformed", target = "target", learn_rate=".0025", max_iter=200000, features = ["sepal_length", "sepal_width", "petal_width", "petal_length"])
    print(regression.query())




    pass
if __name__ == "__main__":
    main()





"""
WITH transformed AS (
	SELECT 
		S.*, 
		cast(CASE WHEN S.iris = 'setosa' THEN 0.0 WHEN S.iris = 'versicolor' then 1.0 when s.iris='virginica' then 2.0 END as double) AS target
	FROM samples AS S 
	order by sepal_length
),
training AS (
  SELECT  t.*, row_number() over() as row FROM transformed as t ORDER BY random()
),

rates (learn_rate, count) as (select 0.0021 as learn_rate, (select count(*) from training) as count from sysibm.sysdummy1),

learning (iteration,b1,b2,b3,intercept,  mse, m1,m2,m3, c) as 
(
select 1, cast(0.05 as double),cast(0.05 as double), cast(0.05 as double), cast(0.2 as double),0.0, cast(0.0 as double),cast(0.0 as double), cast(0.0 as double), cast(0.0 as double) from sysibm.sysdummy1
	union all
select a.iteration + 1, a.m1,a.m2,a.m3, a.c, t.mse, t.m1,t.m2,t.m3, t.c
from 
  learning a
, TABLE 
(
  select 
  a.iteration as iteration,
  avg((train.target-((train.sepal_length*a.b1)+a.intercept+(train.sepal_width*a.b2) +(train.petal_width*a.b3)))*(train.target-((train.sepal_length*a.b1)+a.intercept+(train.sepal_width*a.b2)+(train.petal_width*a.b3)))) as mse,
  a.m1 -(sum((((train.sepal_length*a.b1)+(train.sepal_width*a.b2)+(train.petal_width*a.b3)+a.intercept)-train.target)*train.sepal_length)/(select count from rates)) *(select learn_rate from rates)  as m1,
  a.m1 -(sum((((train.sepal_length*a.m1)+(train.sepal_width*a.m2)+(train.petal_width*a.m3)+a.intercept)-train.target)*train.sepal_length)/(select count from rates))*(select learn_rate from rates) as m1,

  a.m2 -(sum((((train.sepal_width *a.b2)+a.intercept+(train.sepal_length*a.b1)+(train.petal_width*a.b3))-train.target)*train.sepal_width)/(select count from rates)) *(select learn_rate from rates)  as m2,
  a.m3 -(sum((((train.sepal_width *a.b2)+a.intercept+(train.sepal_length*a.b1)+(train.petal_width*a.b3))-train.target)*train.petal_width)/(select count from rates)) *(select learn_rate from rates)  as m3,
  a.c- (sum((((train.sepal_length *a.b1)+a.intercept+(train.sepal_width*a.b2) +(train.petal_width*a.b3) )-train.target))/(select count from rates))*(select learn_rate from rates)  as c
a.c -  (sum((((train.sepal_length*a.m1 )+(train.sepal_width*a.m2)+(train.petal_width*a.m3)+a.intercept)-train.target))/(select count from rates))*(select learn_rate from rates) as c 

  from training as train 
) t
where a.iteration < 100000
)
select * from learning order by mse

"""
