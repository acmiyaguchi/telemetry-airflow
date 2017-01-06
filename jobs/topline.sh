#!/bin/bash

if [[ -z "$report_date" || -z "$mode" ]]; then
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
             --class com.mozilla.telemetry.views.MainSummaryView \
             target/scala-2.11/telemetry-batch-view-1.1.jar \
             --report_date $report_date \
             --mode $mode \
             $sample_option
