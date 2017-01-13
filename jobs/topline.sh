#!/bin/bash

if [[ -z "$report_start" || -z "$mode" ]]; then
   echo "Missing arguments!" 1>&2
   exit 1
fi

if [[ "$sample" ]]; then
    sample_option="--sample $sample"
fi

git clone https://github.com/acmiyaguchi/telemetry-batch-view.git
cd telemetry-batch-view
git checkout topline-report

sbt assembly
spark-submit --master yarn \
             --deploy-mode client \
             --class com.mozilla.telemetry.views.ToplineSummary \
             target/scala-2.11/telemetry-batch-view-1.1.jar \
             --report_start $report_start \
             --mode $mode \
             $sample_option


# Download logs for extracting useful metrics from history. This is done by
# using the history-server api to download the logs as a zip file. All the
# responses from the rest api are in JSON.
# http://stackoverflow.com/questions/1955505/parsing-json-with-unix-tools

if [[ -z "$sample" ]]; then
    sample=100
fi

eventlog="topline_eventlog_${mode}_${instances}_${sample}.zip"
app_id=`curl -s 'localhost:18080/api/v1/applications' | \
    python -c "import sys, json; print json.load(sys.stdin)[0]['id']"`

curl -o $eventlog localhost:18080/api/v1/applications/$app_id/logs

s3_bucket="net-mozaws-prod-us-west-2-pipeline-analysis"
s3_key="amiyaguchi/topline_perf/logs"
s3_path="s3://$s3_bucket/$s3_key/$eventlog"

echo "Saving eventlogs for $app_id to $s3_path"
aws s3 cp $eventlog $s3_path
