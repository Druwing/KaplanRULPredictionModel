import json
import os
import uuid
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")
sns = boto3.client("sns")


def lambda_handler(event, context):
    bucket = os.environ["S3_BUCKET"]
    threshold = float(os.environ.get("RISK_THRESHOLD_HOURS", "720"))
    predicted = float(event["rul_predicted_hours"])
    risk = predicted <= threshold
    record = dict(event)
    record["risk_flag_lambda"] = risk
    record["lambda_received_utc"] = datetime.now(timezone.utc).isoformat()

    turbine = str(record.get("turbine", "unknown")).replace("/", "_")
    key = (
        f"kaplan-rul/{turbine}/"
        f"{record['lambda_received_utc'].replace(':', '-')}-{uuid.uuid4().hex}.json"
    )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(record, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )

    if risk and bool(record.get("risk_transition", False)):
        topic = os.environ.get("SNS_TOPIC_ARN", "")
        if topic:
            sns.publish(
                TopicArn=topic,
                Subject=f"Alerta RUL sintético — {turbine}"[:100],
                Message=(
                    f"Demonstração sintética: RUL previsto {predicted:.1f} h; "
                    f"limite {threshold:.1f} h. Revisão humana necessária. "
                    f"Histórico S3: s3://{bucket}/{key}"
                ),
            )

    return {
        "statusCode": 200,
        "body": json.dumps({"stored": True, "risk": risk, "s3_key": key}),
    }
