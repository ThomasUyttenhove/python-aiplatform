# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import proto
from typing import (
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import _explanation_utils
from google.cloud.aiplatform.compat.services import (
    deployment_resource_pool_service_client_v1beta1,
    endpoint_service_client
)

from google.cloud.aiplatform.compat.types import (
    deployed_model_ref_v1beta1 as gca_deployed_model_ref_compat,
    deployment_resource_pool_v1beta1 as gca_deployment_resource_pool_compat,
    endpoint_v1beta1 as gca_endpoint_compat,
    machine_resources_v1beta1 as gca_machine_resources_compat,
    model_v1beta1 as gca_model_compat,
)

_DEFAULT_MACHINE_TYPE = "n1-standard-2"

_LOGGER = base.Logger(__name__)


class DeploymentResourcePool(base.VertexAiResourceNounWithFutureManager):
    client_class = utils.DeploymentResourcePoolClientWithOverride
    _resource_noun = "deploymentResourcePools"
    _getter_method = "get_deployment_resource_pool"
    _list_method = "list_deployment_resource_pools"
    _delete_method = "delete_deployment_resource_pool"
    _parse_resource_name_method = "parse_deployment_resource_pool_path"
    _format_resource_name_method = "deployment_resource_pool_path"

    def __init__(
        self,
        deployment_resource_pool_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves a DeploymentResourcePool.

        Args:
            deployment_resource_pool_name (str):
                Required. The fully-qualified resource name of the deployment
                resource pool. Example:
                "projects/123/locations/us-central1/deploymentResourcePools/456"
                or "456" when project and location are initialized or passed.
            project (str):
                Optional. Project containing the deployment resource pool to
                retrieve. If not set, the project given to `aiplatform.init`
                will be used.
            location (str):
                Optional. Location containing the deployment resource pool to
                retrieve. If not set, the location given to `aiplatform.init`
                will be used.
            credentials: Optional[auth_credentials.Credentials]=None,
                Custom credentials to use to retrieve the deployment resource
                pool. If not set, the credentials given to `aiplatform.init`
                will be used.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=deployment_resource_pool_name,
        )

        deployment_resource_pool_name = utils.full_resource_name(
            resource_name=deployment_resource_pool_name,
            resource_noun=self._resource_noun,
            parse_resource_name_method=self._parse_resource_name,
            format_resource_name_method=self._format_resource_name,
            project=project,
            location=location,
        )

        self._gca_resource = self._get_gca_resource(
            resource_name=deployment_resource_pool_name
        )

    @classmethod
    def create(
        cls,
        deployment_resource_pool_id: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        credentials: Optional[auth_credentials.Credentials] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        sync=True,
        create_request_timeout: Optional[float] = None,
    ) -> "DeploymentResourcePool":
        """Creates a new DeploymentResourcePool.

        Args:
            deployment_resource_pool_id (str):
                Required. User-specified name for the new deployment resource
                pool.
            project (str):
                Optional. Project containing the deployment resource pool to
                retrieve. If not set, the project given to `aiplatform.init`
                will be used.
            location (str):
                Optional. Location containing the deployment resource pool to
                retrieve. If not set, the location given to `aiplatform.init`
                will be used.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            credentials: Optional[auth_credentials.Credentials]=None,
                Optional. Custom credentials to use to retrieve the deployment
                resource pool. If not set, the credentials given to
                `aiplatform.init` will be used.
            machine_type (str):
                Optional. Machine type to use for the deployment resource pool.
                If not set, the default machine type of `n1-standard-2` is
                used.
            min_replica_count (int):
                Optional. The minimum replica count of the new deployment
                resource pool. Each replica serves a copy of each model deployed
                on the deployment resource pool. If this value is less than
                `max_replica_count`, then autoscaling is enabled, and the actual
                number of replicas will be adjusted to bring resource usage in
                line with the autoscaling targets.
            max_replica_count (int):
                Optional. The maximum replica count of the new deployment
                resource pool.
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_
                count if used. One of NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, or
                NVIDIA_TESLA_A100.
            accelerator_count (int):
                Optional. The number of accelerators attached to each replica.
            autoscaling_target_cpu_utilization (int):
                Optional. Target CPU utilization value for autoscaling. A
                default value of 60 will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int):
                Optional. Target accelerator duty cycle percentage to use for
                autoscaling. Must also set accelerator_type and accelerator
                count if specified. A default value of 60 will be used if
                accelerators are requested and this is not specified.
            sync (bool):
                Optional. Whether to execute this method synchronously. If
                False, this method will be executed in a concurrent Future and
                any downstream object will be immediately returned and synced
                when the Future has completed.
            create_request_timeout (float):
                Optional. The create request timeout in seconds.

        Returns:
            DeploymentResourcePool
        """

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        project = project or initializer.global_config.project
        location = location or initializer.global_config.location

        return cls._create(
            api_client=api_client,
            deployment_resource_pool_id=deployment_resource_pool_id,
            project=project,
            location=location,
            metadata=metadata,
            credentials=credentials,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
            sync=sync,
            create_request_timeout=create_request_timeout,
        )

    @classmethod
    @base.optional_sync()
    def _create(
        cls,
        api_client: deployment_resource_pool_service_client_v1beta1.DeploymentResourcePoolServiceClient,
        deployment_resource_pool_id: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        credentials: Optional[auth_credentials.Credentials] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        sync=True,
        create_request_timeout: Optional[float] = None,
    ) -> "DeploymentResourcePool":
        """Creates a new DeploymentResourcePool.

        Args:
            api_client (DeploymentResourcePoolServiceClient):
                Required. DeploymentResourcePoolServiceClient used to make the
                underlying CreateDeploymentResourcePool API call.
            deployment_resource_pool_id (str):
                Required. User-specified name for the new deployment resource
                pool.
            project (str):
                Optional. Project containing the deployment resource pool to
                retrieve. If not set, the project given to `aiplatform.init`
                will be used.
            location (str):
                Optional. Location containing the deployment resource pool to
                retrieve. If not set, the location given to `aiplatform.init`
                will be used.
            metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as
                metadata.
            credentials: Optional[auth_credentials.Credentials]=None,
                Optional. Custom credentials to use to retrieve the deployment
                resource pool. If not set, the credentials given to
                `aiplatform.init` will be used.
            machine_type (str):
                Optional. Machine type to use for the deployment resource pool.
                If not set, the default machine type of `n1-standard-2` is
                used.
            min_replica_count (int):
                Optional. The minimum replica count of the new deployment
                resource pool. Each replica serves a copy of each model deployed
                on the deployment resource pool. If this value is less than
                `max_replica_count`, then autoscaling is enabled, and the actual
                number of replicas will be adjusted to bring resource usage in
                line with the autoscaling targets.
            max_replica_count (int):
                Optional. The maximum replica count of the new deployment
                resource pool.
            accelerator_type (str):
                Optional. Hardware accelerator type. Must also set accelerator_
                count if used. One of NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
                NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4, or
                NVIDIA_TESLA_A100.
            accelerator_count (int):
                Optional. The number of accelerators attached to each replica.
            autoscaling_target_cpu_utilization (int):
                Optional. Target CPU utilization value for autoscaling. A
                default value of 60 will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int):
                Optional. Target accelerator duty cycle percentage to use for
                autoscaling. Must also set accelerator_type and accelerator
                count if specified. A default value of 60 will be used if
                accelerators are requested and this is not specified.
            sync (bool):
                Optional. Whether to execute this method synchronously. If
                False, this method will be executed in a concurrent Future and
                any downstream object will be immediately returned and synced
                when the Future has completed.
            create_request_timeout (float):
                Optional. The create request timeout in seconds.

        Returns:
            DeploymentResourcePool
        """

        parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        dedicated_resources = gca_machine_resources_compat.DedicatedResources(
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
        )

        machine_spec = gca_machine_resources_compat.MachineSpec(
            machine_type=machine_type
        )

        if autoscaling_target_cpu_utilization:
            autoscaling_metric_spec = (
                gca_machine_resources_compat.AutoscalingMetricSpec(
                    metric_name=(
                        "aiplatform.googleapis.com/prediction/online/cpu/utilization"
                    ),
                    target=autoscaling_target_cpu_utilization,
                )
            )
            dedicated_resources.autoscaling_metric_specs.extend(
                [autoscaling_metric_spec]
            )

        if accelerator_type and accelerator_count:
            utils.validate_accelerator_type(accelerator_type)
            machine_spec.accelerator_type = accelerator_type
            machine_spec.accelerator_count = accelerator_count

            if autoscaling_target_accelerator_duty_cycle:
                autoscaling_metric_spec = gca_machine_resources_compat.AutoscalingMetricSpec(
                    metric_name="aiplatform.googleapis.com/prediction/online/accelerator/duty_cycle",
                    target=autoscaling_target_accelerator_duty_cycle,
                )
                dedicated_resources.autoscaling_metric_specs.extend(
                    [autoscaling_metric_spec]
                )

        dedicated_resources.machine_spec = machine_spec

        gapic_drp = gca_deployment_resource_pool_compat.DeploymentResourcePool(
            dedicated_resources=dedicated_resources
        )

        operation_future = api_client.create_deployment_resource_pool(
            parent=parent,
            deployment_resource_pool=gapic_drp,
            deployment_resource_pool_id=deployment_resource_pool_id,
            metadata=metadata,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_with_lro(cls, operation_future)

        created_drp = operation_future.result()

        _LOGGER.log_create_complete(cls, created_drp, "deployment resource pool")

        return cls._construct_sdk_resource_from_gapic(
            gapic_resource=created_drp,
            project=project,
            location=location,
            credentials=credentials,
        )

    @classmethod
    def list(
        cls,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["models.DeploymentResourcePool"]:
        """Lists the deployment resource pools.

        filter (str):
            Optional. An expression for filtering the results of the request.
            For field names both snake_case and camelCase are supported.
        order_by (str):
            Optional. A comma-separated list of fields to order by, sorted in
            ascending order. Use "desc" after a field name for descending.
            Supported fields: `display_name`, `create_time`, `update_time`
        project (str):
            Optional. Project to retrieve list from. If not set, project
            set in aiplatform.init will be used.
        location (str):
            Optional. Location to retrieve list from. If not set, location
            set in aiplatform.init will be used.
        credentials (auth_credentials.Credentials):
            Optional. Custom credentials to use to retrieve list. Overrides
            credentials set in aiplatform.init.

        Returns:
            List of deployment resource pools.
        """
        return cls._list(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
        )

    def query_deployed_models(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List[gca_deployed_model_ref_compat.DeployedModelRef]:
        project = project or initializer.global_config.project
        location = location or initializer.global_config.location
        api_client = DeploymentResourcePool._instantiate_client(
            location=location, credentials=credentials
        )
        return list(
            api_client.query_deployed_models(
                deployment_resource_pool=self.resource_name
            )
        )

    @classmethod
    def _construct_sdk_resource_from_gapic(
        cls,
        gapic_resource: proto.Message,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "models.DeploymentResourcePool":
        drp = cls._empty_constructor(
            project=project, location=location, credentials=credentials
        )
        drp._gca_resource = gapic_resource
        return drp


class Endpoint(aiplatform.Endpoint):
    @staticmethod
    def _validate_deploy_args(
        min_replica_count: int,
        max_replica_count: int,
        accelerator_type: Optional[str],
        deployed_model_display_name: Optional[str],
        traffic_split: Optional[Dict[str, int]],
        traffic_percentage: Optional[int],
        deployment_resource_pool: Optional[DeploymentResourcePool],
    ):
        """Helper method to validate deploy arguments.

        Args:
            min_replica_count (int): Required. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Required. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Required. Hardware accelerator type. One of
              ACCELERATOR_TYPE_UNSPECIFIED, NVIDIA_TESLA_K80, NVIDIA_TESLA_P100,
              NVIDIA_TESLA_V100, NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            deployed_model_display_name (str): Required. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              and machine spec arguments.

        Raises:
            ValueError: if Min or Max replica is negative. Traffic percentage > 100
            or < 0. Or if traffic_split does not sum to 100.
        """
        if min_replica_count < 0:
            raise ValueError("Min replica cannot be negative.")
        if max_replica_count < 0:
            raise ValueError("Max replica cannot be negative.")
        if deployed_model_display_name is not None:
            utils.validate_display_name(deployed_model_display_name)

        if traffic_split is None:
            if traffic_percentage > 100:
                raise ValueError("Traffic percentage cannot be greater than 100.")
            if traffic_percentage < 0:
                raise ValueError("Traffic percentage cannot be negative.")

        elif traffic_split:
            if sum(traffic_split.values()) != 100:
                raise ValueError(
                    "Sum of all traffic within traffic split needs to be 100."
                )

        # Raises ValueError if invalid accelerator
        if accelerator_type and not deployment_resource_pool:
            utils.validate_accelerator_type(accelerator_type)

    def deploy(
        self,
        model: "Model",
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: int = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_metadata: Optional[aiplatform.explain.ExplanationMetadata] = None,
        explanation_parameters: Optional[
            aiplatform.explain.ExplanationParameters
        ] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync=True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> None:
        """Deploys a Model to the Endpoint.

        Args:
            model (aiplatform.Model): Required. Model to be deployed.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_metadata (aiplatform.explain.ExplanationMetadata): Optional.
              Metadata describing the Model's input and output for explanation.
              `explanation_metadata` is optional while `explanation_parameters` must
              be specified when used. For more details, see `Ref docs
              <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
              Optional. Parameters to configure explaining for Model's predictions.
              For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Target CPU Utilization to use
              for Autoscaling Replicas. A default value of 60 will be used if not
              specified.
            autoscaling_target_accelerator_duty_cycle (int): Target Accelerator Duty
              Cycle. Must also set accelerator_type and accelerator_count if
              specified. A default value of 60 will be used if not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              and machine spec arguments.
        """
        self._sync_gca_resource_if_skipped()

        self._validate_deploy_args(
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            deployed_model_display_name=deployed_model_display_name,
            traffic_split=traffic_split,
            traffic_percentage=traffic_percentage,
            deployment_resource_pool=deployment_resource_pool,
        )

        explanation_spec = _explanation_utils.create_and_validate_explanation_spec(
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
        )

        self._deploy(
            model=model,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            service_account=service_account,
            explanation_spec=explanation_spec,
            metadata=metadata,
            sync=sync,
            deploy_request_timeout=deploy_request_timeout,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
            deployment_resource_pool=deployment_resource_pool,
        )

    @base.optional_sync()
    def _deploy(
        self,
        model: "Model",
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: Optional[int] = 1,
        max_replica_count: Optional[int] = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_spec: Optional[aiplatform.explain.ExplanationSpec] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync=True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> None:
        """Deploys a Model to the Endpoint.

        Args:
            model (aiplatform.Model): Required. Model to be deployed.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_spec (aiplatform.explain.ExplanationSpec): Optional.
              Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Target CPU Utilization to use
              for Autoscaling Replicas. A default value of 60 will be used if not
              specified.
            autoscaling_target_accelerator_duty_cycle (int): Target Accelerator Duty
              Cycle. Must also set accelerator_type and accelerator_count if
              specified. A default value of 60 will be used if not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              and machine spec arguments.
        """
        _LOGGER.log_action_start_against_resource(
            f"Deploying Model {model.resource_name} to", "", self
        )

        self._deploy_call(
            api_client=self.api_client,
            endpoint_resource_name=self.resource_name,
            model=model,
            endpoint_resource_traffic_split=self._gca_resource.traffic_split,
            network=self.network,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            service_account=service_account,
            explanation_spec=explanation_spec,
            metadata=metadata,
            deploy_request_timeout=deploy_request_timeout,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
            deployment_resource_pool=deployment_resource_pool,
        )

        _LOGGER.log_action_completed_against_resource("model", "deployed", self)

        self._sync_gca_resource()

    @classmethod
    def _deploy_call(
        cls,
        api_client: endpoint_service_client.EndpointServiceClient,
        endpoint_resource_name: str,
        model: "Model",
        endpoint_resource_traffic_split: Optional[proto.MapField] = None,
        network: Optional[str] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_spec: Optional[aiplatform.explain.ExplanationSpec] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ):
        """Helper method to deploy model to endpoint.

        Args:
            api_client (endpoint_service_client.EndpointServiceClient): Required.
              endpoint_service_client.EndpointServiceClient to make call.
            endpoint_resource_name (str): Required. Endpoint resource name to deploy
              model to.
            model (aiplatform.Model): Required. Model to be deployed.
            endpoint_resource_traffic_split (proto.MapField): Optional. Endpoint
              current resource traffic split.
            network (str): Optional. The full name of the Compute Engine network to
              which this Endpoint will be peered. E.g.
              "projects/123/global/networks/my_vpc". Private services access must
              already be configured for the network.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the larger value of min_replica_count or 1 will
              be used. If value provided is smaller than min_replica_count, it will
              automatically be increased to be min_replica_count.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_spec (aiplatform.explain.ExplanationSpec): Optional.
              Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Optional. Target CPU
              Utilization to use for Autoscaling Replicas. A default value of 60
              will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int): Optional. Target
              Accelerator Duty Cycle. Must also set accelerator_type and
              accelerator_count if specified. A default value of 60 will be used if
              not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              and machine spec arguments.

        Raises:
            ValueError: If only `accelerator_type` or `accelerator_count` is
            specified.
            ValueError: If model does not support deployment.
            ValueError: If there is not current traffic split and traffic percentage
                is not 0 or 100.
        """

        max_replica_count = max(min_replica_count, max_replica_count)

        if not deployment_resource_pool:
            if bool(accelerator_type) != bool(accelerator_count):
                raise ValueError(
                    "Both `accelerator_type` and `accelerator_count` should be"
                    " specified or None."
                )

            if autoscaling_target_accelerator_duty_cycle is not None and (
                not accelerator_type or not accelerator_count
            ):
                raise ValueError(
                    "Both `accelerator_type` and `accelerator_count` should be set "
                    "when specifying autoscaling_target_accelerator_duty_cycle`"
                )

        deployed_model = gca_endpoint_compat.DeployedModel(
            model=model.versioned_resource_name,
            display_name=deployed_model_display_name,
            service_account=service_account,
        )

        supports_automatic_resources = (
            gca_model_compat.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            in model.supported_deployment_resources_types
        )
        supports_dedicated_resources = (
            gca_model_compat.Model.DeploymentResourcesType.DEDICATED_RESOURCES
            in model.supported_deployment_resources_types
        )
        provided_custom_machine_spec = (
            machine_type
            or accelerator_type
            or accelerator_count
            or autoscaling_target_accelerator_duty_cycle
            or autoscaling_target_cpu_utilization
        )

        # If the model supports both automatic and dedicated deployment resources,
        # decide based on the presence of machine spec customizations
        use_dedicated_resources = (
            supports_dedicated_resources
            and (not supports_automatic_resources or provided_custom_machine_spec)
            and not deployment_resource_pool
        )

        if provided_custom_machine_spec and not use_dedicated_resources:
            _LOGGER.info(
                "Model does not support dedicated deployment resources. "
                "The machine_type, accelerator_type and accelerator_count,"
                "autoscaling_target_accelerator_duty_cycle,"
                "autoscaling_target_cpu_utilization parameters are ignored."
            )

        if use_dedicated_resources and not machine_type:
            machine_type = _DEFAULT_MACHINE_TYPE
            _LOGGER.info(f"Using default machine_type: {machine_type}")

        if use_dedicated_resources:
            dedicated_resources = gca_machine_resources_compat.DedicatedResources(
                min_replica_count=min_replica_count,
                max_replica_count=max_replica_count,
            )

            machine_spec = gca_machine_resources_compat.MachineSpec(
                machine_type=machine_type
            )

            if autoscaling_target_cpu_utilization:
                autoscaling_metric_spec = gca_machine_resources_compat.AutoscalingMetricSpec(
                    metric_name=(
                        "aiplatform.googleapis.com/prediction/online/cpu/utilization"
                    ),
                    target=autoscaling_target_cpu_utilization,
                )
                dedicated_resources.autoscaling_metric_specs.extend(
                    [autoscaling_metric_spec]
                )

            if accelerator_type and accelerator_count:
                utils.validate_accelerator_type(accelerator_type)
                machine_spec.accelerator_type = accelerator_type
                machine_spec.accelerator_count = accelerator_count

                if autoscaling_target_accelerator_duty_cycle:
                    autoscaling_metric_spec = gca_machine_resources_compat.AutoscalingMetricSpec(
                        metric_name="aiplatform.googleapis.com/prediction/online/accelerator/duty_cycle",
                        target=autoscaling_target_accelerator_duty_cycle,
                    )
                    dedicated_resources.autoscaling_metric_specs.extend(
                        [autoscaling_metric_spec]
                    )

            dedicated_resources.machine_spec = machine_spec
            deployed_model.dedicated_resources = dedicated_resources

        elif supports_automatic_resources:
            deployed_model.automatic_resources = (
                gca_machine_resources_compat.AutomaticResources(
                    min_replica_count=min_replica_count,
                    max_replica_count=max_replica_count,
                )
            )
        elif deployment_resource_pool:
            deployed_model.shared_resources = deployment_resource_pool.resource_name
        else:
            raise ValueError(
                "Model does not support deployment. "
                "See https://cloud.google.com/vertex-ai/docs/reference/rpc/google.cloud.aiplatform.v1#google.cloud.aiplatform.v1.Model.FIELDS.repeated.google.cloud.aiplatform.v1.Model.DeploymentResourcesType.google.cloud.aiplatform.v1.Model.supported_deployment_resources_types"
            )

        deployed_model.explanation_spec = explanation_spec

        # Checking if traffic percentage is valid
        # TODO(b/221059294) PrivateEndpoint should support traffic split
        if traffic_split is None and not network:
            # new model traffic needs to be 100 if no pre-existing models
            if not endpoint_resource_traffic_split:
                # default scenario
                if traffic_percentage == 0:
                    traffic_percentage = 100
                # verify user specified 100
                elif traffic_percentage < 100:
                    raise ValueError(
                        """There are currently no deployed models so the traffic
                        percentage for this deployed model needs to be 100."""
                    )
            traffic_split = cls._allocate_traffic(
                traffic_split=dict(endpoint_resource_traffic_split),
                traffic_percentage=traffic_percentage,
            )

        operation_future = api_client.select_version("v1beta1").deploy_model(
            endpoint=endpoint_resource_name,
            deployed_model=deployed_model,
            traffic_split=traffic_split,
            metadata=metadata,
            timeout=deploy_request_timeout,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Deploy", "model", cls, operation_future
        )

        operation_future.result(timeout=None)


class Model(aiplatform.Model):
    def deploy(
        self,
        endpoint: Optional[Union["Endpoint", models.PrivateEndpoint]] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_metadata: Optional[aiplatform.explain.ExplanationMetadata] = None,
        explanation_parameters: Optional[
            aiplatform.explain.ExplanationParameters
        ] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        network: Optional[str] = None,
        sync=True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> Union[Endpoint, models.PrivateEndpoint]:
        """Deploys model to endpoint.

        Endpoint will be created if unspecified.

        Args:
            endpoint (Union[Endpoint, models.PrivateEndpoint]): Optional. Public or
              private Endpoint to deploy model to. If not specified, endpoint
              display name will be model display name+'_endpoint'.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the smaller value of min_replica_count or 1
              will be used.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_metadata (aiplatform.explain.ExplanationMetadata): Optional.
              Metadata describing the Model's input and output for explanation.
              `explanation_metadata` is optional while `explanation_parameters` must
              be specified when used. For more details, see `Ref docs
              <http://tinyurl.com/1igh60kt>`
            explanation_parameters (aiplatform.explain.ExplanationParameters):
              Optional. Parameters to configure explaining for Model's predictions.
              For more details, see `Ref docs <http://tinyurl.com/1an4zake>`
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            encryption_spec_key_name (Optional[str]): Optional. The Cloud KMS
              resource identifier of the customer managed encryption key used to
              protect the model. Has the
                form:
                  ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                  The key needs to be in the same region as where the compute
                  resource is created.  If set, this Endpoint and all sub-resources
                  of this Endpoint will be secured by this key.  Overrides
                  encryption_spec_key_name set in aiplatform.init.
            network (str): Optional. The full name of the Compute Engine network to
              which the Endpoint, if created, will be peered to. E.g.
              "projects/12345/global/networks/myVPC". Private services access must
              already be configured for the network. If set or
              aiplatform.init(network=...) has been set, a PrivateEndpoint will be
              created. If left unspecified, an Endpoint will be created. Read more
              about PrivateEndpoints [in the
              documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints).
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Optional. Target CPU
              Utilization to use for Autoscaling Replicas. A default value of 60
              will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int): Optional. Target
              Accelerator Duty Cycle. Must also set accelerator_type and
              accelerator_count if specified. A default value of 60 will be used if
              not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              and machine spec arguments.

        Returns:
            endpoint (Union[Endpoint, models.PrivateEndpoint]):
                Endpoint with the deployed model.

        Raises:
            ValueError: If `traffic_split` is set for PrivateEndpoint.
        """
        network = network or initializer.global_config.network

        Endpoint._validate_deploy_args(
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            deployed_model_display_name=deployed_model_display_name,
            traffic_split=traffic_split,
            traffic_percentage=traffic_percentage,
            deployment_resource_pool=deployment_resource_pool,
        )

        if isinstance(endpoint, models.PrivateEndpoint):
            if traffic_split:
                raise ValueError(
                    "Traffic splitting is not yet supported for PrivateEndpoint. "
                    "Try calling deploy() without providing `traffic_split`. "
                    "A maximum of one model can be deployed to each private Endpoint."
                )

        explanation_spec = _explanation_utils.create_and_validate_explanation_spec(
            explanation_metadata=explanation_metadata,
            explanation_parameters=explanation_parameters,
        )

        return self._deploy(
            endpoint=endpoint,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            service_account=service_account,
            explanation_spec=explanation_spec,
            metadata=metadata,
            encryption_spec_key_name=encryption_spec_key_name
            or initializer.global_config.encryption_spec_key_name,
            network=network,
            sync=sync,
            deploy_request_timeout=deploy_request_timeout,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
            deployment_resource_pool=deployment_resource_pool,
        )

    @base.optional_sync(return_input_arg="endpoint", bind_future_to_self=False)
    def _deploy(
        self,
        endpoint: Optional[Union["Endpoint", models.PrivateEndpoint]] = None,
        deployed_model_display_name: Optional[str] = None,
        traffic_percentage: Optional[int] = 0,
        traffic_split: Optional[Dict[str, int]] = None,
        machine_type: Optional[str] = None,
        min_replica_count: int = 1,
        max_replica_count: int = 1,
        accelerator_type: Optional[str] = None,
        accelerator_count: Optional[int] = None,
        service_account: Optional[str] = None,
        explanation_spec: Optional[aiplatform.explain.ExplanationSpec] = None,
        metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        network: Optional[str] = None,
        sync: bool = True,
        deploy_request_timeout: Optional[float] = None,
        autoscaling_target_cpu_utilization: Optional[int] = None,
        autoscaling_target_accelerator_duty_cycle: Optional[int] = None,
        deployment_resource_pool: Optional[DeploymentResourcePool] = None,
    ) -> Union[Endpoint, models.PrivateEndpoint]:
        """Deploys model to endpoint.

        Endpoint will be created if unspecified.

        Args:
            endpoint (Union[Endpoint, PrivateEndpoint]): Optional. Public or private
              Endpoint to deploy model to. If not specified, endpoint display name
              will be model display name+'_endpoint'.
            deployed_model_display_name (str): Optional. The display name of the
              DeployedModel. If not provided upon creation, the Model's display_name
              is used.
            traffic_percentage (int): Optional. Desired traffic to newly deployed
              model. Defaults to 0 if there are pre-existing deployed models.
              Defaults to 100 if there are no pre-existing deployed models. Negative
              values should not be provided. Traffic of previously deployed models
              at the endpoint will be scaled down to accommodate new deployed
              model's traffic. Should not be provided if traffic_split is provided.
            traffic_split (Dict[str, int]): Optional. A map from a DeployedModel's
              ID to the percentage of this Endpoint's traffic that should be
              forwarded to that DeployedModel. If a DeployedModel's ID is not listed
              in this map, then it receives no traffic. The traffic percentage
              values must add up to 100, or map must be empty if the Endpoint is to
              not accept any traffic at the moment. Key for model being deployed is
              "0". Should not be provided if traffic_percentage is provided.
            machine_type (str): Optional. The type of machine. Not specifying
              machine type will result in model to be deployed with automatic
              resources.
            min_replica_count (int): Optional. The minimum number of machine
              replicas this deployed model will be always deployed on. If traffic
              against it increases, it may dynamically be deployed onto more
              replicas, and as traffic decreases, some of these extra replicas may
              be freed.
            max_replica_count (int): Optional. The maximum number of replicas this
              deployed model may be deployed on when the traffic against it
              increases. If requested value is too large, the deployment will error,
              but if deployment succeeds then the ability to scale the model to that
              many replicas is guaranteed (barring service outages). If traffic
              against the deployed model increases beyond what its replicas at
              maximum may handle, a portion of the traffic will be dropped. If this
              value is not provided, the smaller value of min_replica_count or 1
              will be used.
            accelerator_type (str): Optional. Hardware accelerator type. Must also
              set accelerator_count if used. One of ACCELERATOR_TYPE_UNSPECIFIED,
              NVIDIA_TESLA_K80, NVIDIA_TESLA_P100, NVIDIA_TESLA_V100,
              NVIDIA_TESLA_P4, NVIDIA_TESLA_T4
            accelerator_count (int): Optional. The number of accelerators to attach
              to a worker replica.
            service_account (str): The service account that the DeployedModel's
              container runs as. Specify the email address of the service account.
              If this service account is not specified, the container runs as a
              service account that doesn't have access to the resource project.
              Users deploying the Model must have the `iam.serviceAccounts.actAs`
              permission on this service account.
            explanation_spec (aiplatform.explain.ExplanationSpec): Optional.
              Specification of Model explanation.
            metadata (Sequence[Tuple[str, str]]): Optional. Strings which should be
              sent along with the request as metadata.
            encryption_spec_key_name (Optional[str]): Optional. The Cloud KMS
              resource identifier of the customer managed encryption key used to
              protect the model. Has the
                form:
                  ``projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key``.
                  The key needs to be in the same region as where the compute
                  resource is created.  If set, this Model and all sub-resources of
                  this Model will be secured by this key.  Overrides
                  encryption_spec_key_name set in aiplatform.init
            network (str): Optional. The full name of the Compute Engine network to
              which the Endpoint, if created, will be peered to. E.g.
              "projects/12345/global/networks/myVPC". Private services access must
              already be configured for the network. Read more about
              PrivateEndpoints [in the
              documentation](https://cloud.google.com/vertex-ai/docs/predictions/using-private-endpoints).
            sync (bool): Whether to execute this method synchronously. If False,
              this method will be executed in concurrent Future and any downstream
              object will be immediately returned and synced when the Future has
              completed.
            deploy_request_timeout (float): Optional. The timeout for the deploy
              request in seconds.
            autoscaling_target_cpu_utilization (int): Optional. Target CPU
              Utilization to use for Autoscaling Replicas. A default value of 60
              will be used if not specified.
            autoscaling_target_accelerator_duty_cycle (int): Optional. Target
              Accelerator Duty Cycle. Must also set accelerator_type and
              accelerator_count if specified. A default value of 60 will be used if
              not specified.
            deployment_resource_pool (DeploymentResourcePool): Optional.
              Resource pool where the model will be deployed. All models that
              are deployed to the same DeploymentResourcePool will be hosted in
              a shared model server. If provided, will override replica count
              and machine spec arguments.

        Returns:
            endpoint (Union[Endpoint, models.PrivateEndpoint]):
                Endpoint with the deployed model.
        """

        if endpoint is None:
            display_name = self.display_name[:118] + "_endpoint"

            if not network:
                endpoint = Endpoint.create(
                    display_name=display_name,
                    project=self.project,
                    location=self.location,
                    credentials=self.credentials,
                    encryption_spec_key_name=encryption_spec_key_name,
                )
            else:
                endpoint = models.PrivateEndpoint.create(
                    display_name=display_name,
                    network=network,
                    project=self.project,
                    location=self.location,
                    credentials=self.credentials,
                    encryption_spec_key_name=encryption_spec_key_name,
                )

        _LOGGER.log_action_start_against_resource("Deploying model to", "", endpoint)

        endpoint._deploy_call(
            endpoint.api_client,
            endpoint.resource_name,
            self,
            endpoint._gca_resource.traffic_split,
            network=network,
            deployed_model_display_name=deployed_model_display_name,
            traffic_percentage=traffic_percentage,
            traffic_split=traffic_split,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            accelerator_type=accelerator_type,
            accelerator_count=accelerator_count,
            service_account=service_account,
            explanation_spec=explanation_spec,
            metadata=metadata,
            deploy_request_timeout=deploy_request_timeout,
            autoscaling_target_cpu_utilization=autoscaling_target_cpu_utilization,
            autoscaling_target_accelerator_duty_cycle=autoscaling_target_accelerator_duty_cycle,
            deployment_resource_pool=deployment_resource_pool,
        )

        _LOGGER.log_action_completed_against_resource("model", "deployed", endpoint)

        endpoint._sync_gca_resource()

        return endpoint
