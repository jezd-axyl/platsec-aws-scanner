from logging import getLogger
from typing import List

from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from src.clients.aws_boto_paginator import AwsBotoPaginator
from src.data.aws_scanner_exceptions import ListSSMParametersException
from src.data.aws_ssm_types import Parameter, to_parameter


class AwsSSMClient:
    def __init__(self, boto_ssm: BaseClient):
        self._logger = getLogger(self.__class__.__name__)
        self._ssm = boto_ssm

    def list_parameters(self) -> List[Parameter]:
        try:
            return AwsBotoPaginator(  # type: ignore
                boto_action=self._ssm.describe_parameters,
                boto_args={"ParameterFilters": [{"Key": "Path", "Option": "Recursive", "Values": ["/"]}]},
                boto_max_results=50,
            ).paginate(response_key="Parameters", response_mapper=to_parameter)
        except (BotoCoreError, ClientError) as error:
            raise ListSSMParametersException(error) from None
