from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, trim, coalesce, regexp_replace, translate, when, lit, concat, concat_ws, collect_list, first, current_date, date_sub
)
from pyspark.sql.functions import broadcast
import datetime

# Initialize Spark session
spark = SparkSession.builder.appName("OrderProcessingTest").getOrCreate()

# Hardcoded Sample Data for Testing
ool_data = [
    {"line_id": 92699366, "inventory_item_id": 1001, "ordered_quantity": 2.0, "ordered_item": "ITEM001",
     "attribute1": "Engraving Text", "attribute2": "GC123", "attribute5": "Custom", "attribute9": "12",
     "attribute10": "John", "attribute11": "Jane", "attribute12": "Happy Birthday", "link_to_line_id": None,
     "order_source_id": 1042, "header_id": 5001, "source_document_line_id": 7001},
    {"line_id": 92699367, "inventory_item_id": 1002, "ordered_quantity": 1.0, "ordered_item": "ITEM002",
     "attribute1": None, "attribute2": None, "attribute5": None, "attribute9": None, "attribute10": None,
     "attribute11": None, "attribute12": None, "link_to_line_id": 92699366, "order_source_id": 1021,
     "header_id": 5002, "source_document_line_id": 7002}
]

xsp_data = [
    {"line_id": 92699366, "creation_date": datetime.datetime(2025, 3, 1), "reject_reason": "Quality", "zone_name": "Zone1", "machine_name": "Machine1"},
    {"line_id": 92699367, "creation_date": datetime.datetime(2025, 3, 2), "reject_reason": None, "zone_name": "Zone2", "machine_name": "Machine2"}
]

wnd_data = [{"delivery_id": 196850}, {"delivery_id": 196851}]
wda_data = [{"delivery_detail_id": 1, "delivery_id": 196850}, {"delivery_detail_id": 2, "delivery_id": 196851}]
wdd_data = [{"delivery_detail_id": 1, "source_line_id": 92699366, "source_header_id": 5001},
            {"delivery_detail_id": 2, "source_line_id": 92699367, "source_header_id": 5002}]
ooh_data = [{"header_id": 5001, "source_document_id": 6001}, {"header_id": 5002, "source_document_id": 6002}]
rh_data = [{"requisition_header_id": 6001}, {"requisition_header_id": 6002}]
rl_data = [{"requisition_header_id": 6001, "requisition_line_id": 7001}, {"requisition_header_id": 6002, "requisition_line_id": 7002}]
ad_data = [{"pk1_value": "7001", "document_id": 8001, "entity_name": "REQ_LINES"},
           {"pk1_value": "92699366", "document_id": 8002, "entity_name": "ORDER_LINES"}]
doc_data = [{"document_id": 8001, "category_id": 9001, "media_id": 10001},
            {"document_id": 8002, "category_id": 9002, "media_id": 10002}]
dc_data = [{"category_id": 9001}, {"category_id": 9002}]
lt_data = [{"media_id": 10001, "long_text": "Requisition Note"}, {"media_id": 10002, "long_text": "Order Note"}]
msi_data = [{"inventory_item_id": 1001, "organization_id": 82, "description": "Sample Item 1", "concatenated_segments": "SV-ENG-"},
            {"inventory_item_id": 1002, "organization_id": 82, "description": "Sample Item 2", "concatenated_segments": "SV-GC-"}]
xpe_data = [{"inventory_item_id": 1001, "item_zone_name": "Zone1", "item_zone_code": "Z1C"},
            {"inventory_item_id": 1002, "item_zone_name": "Zone2", "item_zone_code": "Z2C"}]
ool2_data = [
    {"line_id": 92699366, "inventory_item_id": 1001, "ordered_item": "ITEM001", "header_id": 5001},
    {"line_id": 92699367, "inventory_item_id": 1002, "ordered_item": "ITEM002", "header_id": 5002}
]
msi2_data = [
    {"inventory_item_id": 1001, "organization_id": 82, "description": "Kit Component 1"},
    {"inventory_item_id": 1002, "organization_id": 82, "description": "Kit Component 2"}
]
bom_data = [
    {"bill_sequence_id": 1, "assembly_item_id": 1001, "organization_id": 82},
    {"bill_sequence_id": 2, "assembly_item_id": 1002, "organization_id": 82}
]
bic_data = [
    {"bill_sequence_id": 1, "component_item_id": 1001, "component_remarks": "Remark 1", "disable_date": datetime.datetime(2025, 12, 31)},
    {"bill_sequence_id": 2, "component_item_id": 1002, "component_remarks": "Remark 2", "disable_date": None}
]

# Create DataFrames with Aliases
ool_df = spark.createDataFrame(ool_data).alias("ool")
xsp_df = spark.createDataFrame(xsp_data).alias("xsp")
wnd_df = spark.createDataFrame(wnd_data).alias("wnd")
wda_df = spark.createDataFrame(wda_data).alias("wda")
wdd_df = spark.createDataFrame(wdd_data).alias("wdd")
ooh_df = spark.createDataFrame(ooh_data).alias("ooh")
rh_df = spark.createDataFrame(rh_data).alias("rh")
rl_df = spark.createDataFrame(rl_data).alias("rl")
ad_df = spark.createDataFrame(ad_data).alias("ad")
doc_df = spark.createDataFrame(doc_data).alias("doc")
dc_df = spark.createDataFrame(dc_data).alias("dc")
lt_df = spark.createDataFrame(lt_data).alias("lt")
msi_df = spark.createDataFrame(msi_data).alias("msi")
xpe_df = spark.createDataFrame(xpe_data).alias("xpe")
ool2_df = spark.createDataFrame(ool2_data).alias("ool2")
msi2_df = spark.createDataFrame(msi2_data).alias("msi2")
bom_df = spark.createDataFrame(bom_data).alias("bom")
bic_df = spark.createDataFrame(bic_data).alias("bic")

# Core DataFrame for Notes Calculation
core_df = wnd_df.join(wda_df, wnd_df["delivery_id"] == wda_df["delivery_id"], "inner") \
                .join(wdd_df, wda_df["delivery_detail_id"] == wdd_df["delivery_detail_id"], "inner") \
                .join(ooh_df, wdd_df["source_header_id"] == ooh_df["header_id"], "inner") \
                .join(ool_df, (ool_df["header_id"] == ooh_df["header_id"]) &
                              (ool_df["line_id"] == wdd_df["source_line_id"]), "inner") \
                .cache()

# Notes Calculation
# 1. Requisition Notes
req_notes = core_df.join(rh_df, ooh_df["source_document_id"] == rh_df["requisition_header_id"], "inner") \
                   .join(rl_df, (rh_df["requisition_header_id"] == rl_df["requisition_header_id"]) &
                                (ool_df["source_document_line_id"] == rl_df["requisition_line_id"]), "inner") \
                   .join(ad_df.filter(col("entity_name") == "REQ_LINES"),
                         ad_df["pk1_value"] == rl_df["requisition_line_id"].cast("string"), "inner") \
                   .join(doc_df, ad_df["document_id"] == doc_df["document_id"], "inner") \
                   .join(dc_df, doc_df["category_id"] == dc_df["category_id"], "inner") \
                   .join(lt_df, doc_df["media_id"] == lt_df["media_id"], "inner") \
                   .select(wnd_df["delivery_id"], ool_df["line_id"], lt_df["long_text"].alias("notes"))

# 2. Order Line Notes
order_notes = core_df.join(ad_df, ad_df["pk1_value"] == ool_df["line_id"].cast("string"), "inner") \
                     .join(doc_df, ad_df["document_id"] == doc_df["document_id"], "inner") \
                     .join(dc_df, doc_df["category_id"] == dc_df["category_id"], "inner") \
                     .join(lt_df, doc_df["media_id"] == lt_df["media_id"], "inner") \
                     .select(wnd_df["delivery_id"], ool_df["line_id"], lt_df["long_text"].alias("notes"))

# 3. Attribute Notes
attr_notes = core_df.filter(ool_df["attribute10"].isNotNull()) \
                    .select(
                        wnd_df["delivery_id"],
                        ool_df["line_id"],
                        concat(lit("To:      "), ool_df["attribute10"],
                               lit("\n"), ool_df["attribute12"],
                               lit("\nFrom:    "), ool_df["attribute11"]).alias("notes")
                    )

# Combine all notes and aggregate
all_notes = req_notes.union(order_notes).union(attr_notes) \
                     .groupBy("delivery_id", "line_id") \
                     .agg(concat_ws("\n", collect_list("notes")).alias("combined_notes"))

# Kit Item Subquery
kit_items = ool_df.join(ool2_df, ool_df["link_to_line_id"] == ool2_df["line_id"], "left") \
                  .join(msi2_df, ool2_df["inventory_item_id"] == msi2_df["inventory_item_id"], "left") \
                  .filter(msi2_df["organization_id"] == 82) \
                  .groupBy(ool_df["line_id"]) \
                  .agg(first(concat(lit("Kit Item: "), ool2_df["ordered_item"], lit("\n"), msi2_df["description"])).alias("kit_item_notes"))

# BOM Component Remarks Subquery
bom_subquery = ool_df.join(ool2_df, ool_df["link_to_line_id"] == ool2_df["line_id"], "left") \
                     .select(ool_df["line_id"], ool_df["inventory_item_id"].alias("ool_inventory_item_id"),
                             ool2_df["inventory_item_id"].alias("ool2_inventory_item_id"))

bom_remarks = bom_subquery.join(bom_df, bom_subquery["ool2_inventory_item_id"] == bom_df["assembly_item_id"], "left") \
                          .join(bic_df, (bic_df["bill_sequence_id"] == bom_df["bill_sequence_id"]) &
                                        (bic_df["component_item_id"] == bom_subquery["ool_inventory_item_id"]), "left") \
                          .filter((bom_df["organization_id"] == 82) &
                                  (coalesce(bic_df["disable_date"], current_date()) >= current_date())) \
                          .groupBy(bom_subquery["line_id"]) \
                          .agg(first(bic_df["component_remarks"]).alias("bom_remarks"))

# Main DataFrame Joins
base_df = ool_df.join(wdd_df, ool_df["line_id"] == wdd_df["source_line_id"], "inner") \
                .join(wda_df, wdd_df["delivery_detail_id"] == wda_df["delivery_detail_id"], "inner") \
                .join(wnd_df, wda_df["delivery_id"] == wnd_df["delivery_id"], "inner") \
                .join(xsp_df, ool_df["line_id"] == xsp_df["line_id"], "inner") \
                .join(msi_df, (ool_df["inventory_item_id"] == msi_df["inventory_item_id"]) &
                              (msi_df["organization_id"] == 82), "inner") \
                .select(
                    ool_df["line_id"].alias("ool_line_id"),
                    ool_df["inventory_item_id"].alias("ool_inventory_item_id"),
                    ool_df["ordered_quantity"].alias("ool_ordered_quantity"),
                    ool_df["ordered_item"].alias("ool_ordered_item"),
                    ool_df["attribute1"].alias("ool_attribute1"),
                    ool_df["attribute2"].alias("ool_attribute2"),
                    ool_df["attribute5"].alias("ool_attribute5"),
                    ool_df["attribute9"].alias("ool_attribute9"),
                    ool_df["link_to_line_id"].alias("ool_link_to_line_id"),
                    ool_df["order_source_id"].alias("ool_order_source_id"),
                    wnd_df["delivery_id"].alias("wnd_delivery_id"),
                    xsp_df["creation_date"].alias("xsp_creation_date"),
                    xsp_df["reject_reason"].alias("xsp_reject_reason"),
                    xsp_df["zone_name"].alias("xsp_zone_name"),
                    xsp_df["machine_name"].alias("xsp_machine_name"),
                    msi_df["description"].alias("msi_description"),
                    msi_df["concatenated_segments"].alias("msi_concatenated_segments")
                )

# Add Zone Code with Left Outer Join
zone_df = base_df.join(xpe_df,
                       (base_df["ool_inventory_item_id"] == xpe_df["inventory_item_id"]) &
                       (base_df["xsp_zone_name"] == xpe_df["item_zone_name"]),
                       "left_outer") \
                 .select(base_df["*"], xpe_df["item_zone_code"].alias("zone_code"))

# Join with Notes, Kit Items, and BOM Remarks
full_df = zone_df.join(all_notes,
                       (zone_df["wnd_delivery_id"] == all_notes["delivery_id"]) &
                       (zone_df["ool_line_id"] == all_notes["line_id"]), "left_outer") \
                 .join(kit_items, zone_df["ool_line_id"] == kit_items["line_id"], "left_outer") \
                 .join(bom_remarks, zone_df["ool_line_id"] == bom_remarks["line_id"], "left_outer")

# Construct order_line_notes with NULL handling
order_line_notes = trim(
    concat(
        coalesce(
            regexp_replace(translate(col("ool_attribute1"), "‘’", "''"), "[^[:graph:][:blank:]]", ""),
            col("msi_description")
        ),
        coalesce(
            when(col("ool_attribute2").isNotNull(), concat(lit("\n"), lit("Gift Card # "), col("ool_attribute2"))),
            lit("")
        ),
        coalesce(
            when(col("ool_link_to_line_id").isNotNull(), concat(lit("\n"), col("kit_item_notes"))),
            lit("")
        ),
        coalesce(
            when(col("ool_link_to_line_id").isNotNull(), concat(lit("\n"), col("bom_remarks"))),
            lit("")
        ),
        coalesce(
            when(col("ool_order_source_id") == 1042,
                when(col("msi_concatenated_segments") == "SV-ENG-", concat(lit("("), col("ool_attribute5"), lit(")")))
                .when(col("msi_concatenated_segments") == "SV-GC-", concat(lit("("), col("ool_attribute5"), lit(")")))
            ).when(col("ool_order_source_id") == 1021,
                when(col("msi_concatenated_segments") == "SV-GC-", concat(lit("("), col("ool_attribute5"), lit(")")))
            ),
            lit("")
        ),
        lit(" "),
        coalesce(col("combined_notes"), lit("")),
        coalesce(
            when(col("ool_attribute9").isNotNull() & (col("ool_attribute9") != "0000"),
                 concat(lit("\n"), lit("Leather Cord Length: "), col("ool_attribute9"))),
            lit("")
        )
    )
)

# Final Result with Filter
result_df = full_df.select(
    col("xsp_creation_date").alias("creation_date"),
    col("ool_line_id").alias("line_id"),
    col("wnd_delivery_id").alias("delivery_id"),
    col("ool_ordered_quantity").alias("ordered_quantity"),
    col("ool_ordered_item").alias("ordered_item"),
    col("xsp_reject_reason").alias("reject_reason"),
    col("xsp_zone_name").alias("zone_name"),
    col("zone_code"),
    col("xsp_machine_name").alias("machine_name"),
    order_line_notes.alias("order_line_notes")
).filter(col("xsp_creation_date") > date_sub(current_date(), 5))

# Display Results
result_df.show(truncate=False)

# Unpersist Cached DataFrame
core_df.unpersist()

# Stop Spark Session
spark.stop()
