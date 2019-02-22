import argparse
import os
import pprint
import random
import time

from google.cloud import monitoring_v3

# this sample python file creates a metric and does not avoid collisions
#RANDOM_SUFFIX = str(random.randint(1999, 4999))

#use this variable to create a random time series value
RANDOM_FLOAT_NUM = round(random.uniform(5.5, 50.5),2)

# replace instance id and region below plus the create and write_time_series are only tested below

def create_metric_descriptor(project_id):
    # [START monitoring_create_metric]
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(project_id)
    descriptor = monitoring_v3.types.MetricDescriptor()
    descriptor.type = 'custom.googleapis.com/tkcustom-metric-python'
    descriptor.metric_kind = (
        monitoring_v3.enums.MetricDescriptor.MetricKind.GAUGE)
    descriptor.value_type = (
        monitoring_v3.enums.MetricDescriptor.ValueType.DOUBLE)
    descriptor.description = 'TK demo custom metric from python'
    descriptor = client.create_metric_descriptor(project_name, descriptor)
    print('Created {}.'.format(descriptor.name))
    # [END monitoring_create_metric]


def delete_metric_descriptor(descriptor_name):
    # [START monitoring_delete_metric]
    client = monitoring_v3.MetricServiceClient()
    client.delete_metric_descriptor(descriptor_name)
    print('Deleted metric descriptor {}.'.format(descriptor_name))
    # [END monitoring_delete_metric]


def write_time_series(project_id):
    # [START monitoring_write_timeseries]
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(project_id)

    series = monitoring_v3.types.TimeSeries()
    series.metric.type = 'custom.googleapis.com/tkcustom-metric-python'
    series.resource.type = 'gce_instance'
    series.resource.labels['instance_id'] = 'use your instanceid'
    series.resource.labels['zone'] = 'your zone'
    point = series.points.add()
    point.value.double_value = RANDOM_FLOAT_NUM
    now = time.time()
    point.interval.end_time.seconds = int(now)
    point.interval.end_time.nanos = int(
        (now - point.interval.end_time.seconds) * 10**9)
    client.create_time_series(project_name, [series])
    # [END monitoring_write_timeseries]

def list_metric_descriptors(project_id):
    # [START monitoring_list_descriptors]
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(project_id)
    for descriptor in client.list_metric_descriptors(project_name):
        print(descriptor.type)
    # [END monitoring_list_descriptors]
    

class MissingProjectIdError(Exception):
    pass


def project_id():
    """Retreives the project id from the environment variable.

    Raises:
        MissingProjectIdError -- When not set.

    Returns:
        str -- the project name
    """
    project_id = (os.environ['GOOGLE_CLOUD_PROJECT'] or
                  os.environ['GCLOUD_PROJECT'])

    if not project_id:
        raise MissingProjectIdError(
            'Set the environment variable ' +
            'GCLOUD_PROJECT to your Google Cloud Project Id.')
    return project_id


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Demonstrates Monitoring API operations.')

    subparsers = parser.add_subparsers(dest='command')

    create_metric_descriptor_parser = subparsers.add_parser(
        'create-metric-descriptor',
        help=create_metric_descriptor.__doc__
    )

    delete_metric_descriptor_parser = subparsers.add_parser(
        'delete-metric-descriptor',
        help=list_metric_descriptors.__doc__
    )

    delete_metric_descriptor_parser.add_argument(
        '--metric-descriptor-name',
        help='Metric descriptor to delete',
        required=True
    )

    write_time_series_parser = subparsers.add_parser(
        'write-time-series',
        help=write_time_series.__doc__
    )

  

    args = parser.parse_args()

    if args.command == 'create-metric-descriptor':
        create_metric_descriptor(project_id())
    
    if args.command == 'delete-metric-descriptor':
        delete_metric_descriptor(args.metric_descriptor_name)
    
    if args.command == 'write-time-series':
        write_time_series(project_id())
    
