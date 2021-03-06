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

RI_Outages = riOutageRecords.map(lambda p: (p[2],p[4],p[5],p[8],p[12]))  # I could not figure out how to properly parse this...
RI_Weather = weatherRecords.map(lambda p: (p[5],p[6],p[26],p[27],p[28],p[30],p[37],p[38],p[39],p[40],p[41],p[42],p[43],p[44],p[46]))

outageSchemaString = 'DATETIME HR MIN AREA NUMCUSTOMERS'  # If the above gets updated, this would too (of course)
weatherSchemaString = 'DTS ReportType maxTemp minTemp aveTemp aveHumidity WeatherCodes Precip Snowfall SnowDepth aveStationPressure aveSeaLevelPressure aveWindSpeed maxWindSpeed SustainedWindSpeed'

outageFields = [StructField(field_name, StringType(), True) for field_name in outageSchemaString.split()]
weatherFields = [StructField(field_name, StringType(), True) for field_name in weatherSchemaString.split()]

outageSchema = StructType(outageFields)
weatherSchema = StructType(weatherFields)

schemaOutageData = sqlContext.createDataFrame(RI_Outages, outageSchema)
schemaWeatherData = sqlContext.createDataFrame(RI_Weather, weatherSchema)

schemaOutageData.registerTempTable('RI_Outages')
schemaWeatherData.registerTempTable('RI_Weather')

#results_weather = sqlContext.sql('SELECT * FROM RI_Weather WHERE ReportType="SOD" LIMIT 10').show()

#results_outages = sqlContext.sql('SELECT DATETIME, AREA, NUMCUSTOMERS, CONCAT(HR, MIN) as DURATION FROM RI_Outages LIMIT 10')
#results_outages.show()

result_weatherOutage = sqlContext.sql('SELECT to_date(w.DTS) as DT ,w.maxTemp ,w.minTemp ,w.aveTemp ,w.aveHumidity ,w.WeatherCodes ,w.Precip ,w.Snowfall ,w.SnowDepth ,w.aveStationPressure ,w.aveSeaLevelPressure ,w.aveWindSpeed ,w.maxWindSpeed, w.SustainedWindSpeed ,case when o.DATETIME is null then 0 else 1 end as OutageIND  FROM RI_Weather w left outer join RI_Outages o on to_date(w.DTS) = to_date(concat(substr(DATETIME,7,4),"-",substr(DATETIME,1,2),"-",substr(DATETIME,4,2)))   WHERE w.ReportType="SOD" and year(to_date(w.DTS))=2016 and month(to_date(w.DTS))=2  ORDER BY DT  LIMIT 100')
result_weatherOutage.show()



print(steel_thread.random_prediction())
