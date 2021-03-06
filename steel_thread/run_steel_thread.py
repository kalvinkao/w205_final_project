from pyspark.sql import SQLContext
from pyspark.sql.types import *
import steel_thread
from pyspark import SparkContext

sc = SparkContext()
sqlContext = SQLContext(sc)

outageData=sc.textFile("file:///home/w205/steel_thread/outage_history.csv")
weatherData=sc.textFile("file:///home/w205/steel_thread/weather_history.csv")

riOutages = outageData.filter(lambda x: "Rhode Island" in x)
riOutageRecords = riOutages.map(lambda r : r.split(","))
weatherRecords = weatherData.map(lambda r : r.split(","))

RI_Outages = riOutageRecords.map(lambda p: (p[2],p[4],p[5],p[8],p[12]))
RI_Weather = weatherRecords.map(lambda p: (p[5],p[10],p[16], p[17], p[18], p[19]))

outageSchemaString = 'DATETIME HR MIN AREA NUMCUSTOMERS'
weatherSchemaString = 'DATETIME DRYBULBTEMP HUMIDITY WINDSPEED WINDDIRECTION WINDGUSTSPEED'

outageFields = [StructField(field_name, StringType(), True) for field_name in outageSchemaString.split()]
weatherFields = [StructField(field_name, StringType(), True) for field_name in weatherSchemaString.split()]

outageSchema = StructType(outageFields)
weatherSchema = StructType(weatherFields)

schemaOutageData = sqlContext.createDataFrame(RI_Outages, outageSchema)
schemaWeatherData = sqlContext.createDataFrame(RI_Weather, weatherSchema)

schemaOutageData.registerTempTable('RI_Outages')
schemaWeatherData.registerTempTable('RI_Weather')

results_weather = sqlContext.sql('SELECT * FROM RI_Weather LIMIT 10')
results_weather.show()

results_outages = sqlContext.sql('SELECT DATETIME, AREA, NUMCUSTOMERS, CONCAT(HR, MIN) as DURATION FROM RI_Outages LIMIT 10')
results_outages.show()

print(steel_thread.random_prediction())

from pyspark.sql import functions
from pyspark.sql import Row

split_col = functions.split(schemaOutageData['DATETIME'], ' ')
steel_thread_outage_data = schemaOutageData.withColumn('DATETIME', split_col.getItem(0))

weather_dates = schemaWeatherData.select(functions.date_format('DATETIME', 'yyyy-MM-dd HH:mm').alias('date')).collect()
weather_dates_rdd = sc.parallelize(weather_dates)
new_row = Row("date")
l_as_df = weather_dates_rdd.map(new_row).toDF()
schemaWeatherData2 = schemaWeatherData.join(l_as_df)

schemaWeatherData2.registerTempTable('RI_Weather_2')
test = sqlContext.sql('SELECT * FROM RI_Weather_2 WHERE cast (date as date) = "2016-01-01" LIMIT 10')