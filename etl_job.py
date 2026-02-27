from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, hour

# --- Configuration ---
RAW_DATA_PATH = "gs://raw-logs-bucket/raw_logs/2025/10/22/web_server_logs.json"
CLEAN_DATA_OUTPUT_PATH = "gs://raw-logs-bucket/clean_data/aggregated_visits/"

# Initialize Spark Session
spark = SparkSession.builder.appName("WebLogETL").getOrCreate()

# 1. EXTRACT: Read the raw JSON data from GCS
# Spark reads the data in parallel across the cluster
raw_df = spark.read.json(RAW_DATA_PATH)
print("--- Schema of Raw Data ---")
raw_df.printSchema()

# 2. TRANSFORM: Cleaning, Enrichment, and Aggregation
transformed_df = raw_df.select(
    col("timestamp").cast("timestamp").alias("event_time"),
    col("user_id"),
    col("url_path"),
    col("latency_ms").cast("integer").alias("latency_ms")
)

# Filter out bad data (e.g., latency too high) and enrich with hour_of_day
transformed_df = transformed_df.filter(col("latency_ms") < 4000)
transformed_df = transformed_df.withColumn("hour_of_day", hour(col("event_time")))

# Aggregation: Calculate total visits and average latency per URL and hour
aggregated_df = transformed_df.groupBy("url_path", "hour_of_day").agg(
    count("*").alias("total_visits"),
    avg("latency_ms").alias("avg_latency_ms")
)
print("--- Schema of Aggregated Data ---")
aggregated_df.printSchema()

# 3. LOAD: Write the aggregated data back to GCS in Parquet format
# Parquet is a columnar format optimized for analytics and is highly recommended.
aggregated_df.write.mode("overwrite").parquet(CLEAN_DATA_OUTPUT_PATH)

print(f"✅ Aggregated data successfully written to: {CLEAN_DATA_OUTPUT_PATH}")
spark.stop()