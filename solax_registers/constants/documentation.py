from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

STATS_PARAM = OpenApiParameter(
    name="fields",
    location="query",
    required=True,
    description="Fields to return.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Ex. 1",
            summary="Using 'all'",
            value=["all"],
            description="You can use the word 'all' to return all fields.",
        ),
        OpenApiExample(
            name="Ex. 2",
            summary="Passing list of fields",
            value=["upload_time", "grid_voltage_r"],
            description="Finally, you can pass a list of fields.",
        ),
    ],
    many=True,
)

SINCE_PARAM = OpenApiParameter(
    name="since",
    type=OpenApiTypes.DATETIME,
    location="query",
    required=False,
    description="First date in filter range. Optional. If this param "
    "and the `before` param are missing, only the last record will be queried.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Using a datetime value",
            summary="Using a datetime value",
            value="2023-01-01 00:00",
            description="You can use an ISO-8601 format to specify the datetime.",
        ),
        OpenApiExample(
            name="Using a date value",
            summary="Using a date value",
            value="2023-01-01",
            description="You can also pass an ISO-8601 date instead of datetime.",
        ),
        OpenApiExample(
            name="Using 0001-01-01",
            summary="Using 0001-01-01",
            value="0001-01-01",
            description="You can use the date 0001-01-01 and not use the `before` "
            "param to forcefully query the history stats.",
        ),
    ],
)

BEFORE_PARAM = OpenApiParameter(
    name="before",
    type=OpenApiTypes.DATETIME,
    location="query",
    required=False,
    description="First date in filter range. Optional. If this param "
    "and the `before` param are missing, only the last record will be queried.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Using a datetime value",
            summary="Using a datetime value",
            value="2020-01-01 00:00",
            description="You can use an ISO-8601 format to specify the datetime.",
        ),
        OpenApiExample(
            name="Using a date value",
            summary="Using a date value",
            value="2020-01-01",
            description="You can also pass an ISO-8601 date instead of datetime.",
        ),
    ],
)

SINCE_PARAM_WITHOUT_DATETIME = OpenApiParameter(
    name="since",
    type=OpenApiTypes.DATE,
    location="query",
    required=False,
    description="First date in filter range. Optional.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Example",
            summary="Using a date value",
            value="2023-01-01",
            description="You must pass an ISO-8601 date.",
        )
    ],
)

BEFORE_PARAM_WITHOUT_DATETIME = OpenApiParameter(
    name="before",
    type=OpenApiTypes.DATE,
    location="query",
    required=False,
    description="Second date in filter range. Optional.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Ex. 1",
            summary="Using a date value",
            value="2023-01-01",
            description="You must pass an ISO-8601 date.",
        ),
    ],
)

OVERWRITE_PARAM = OpenApiParameter(
    name="overwrite",
    enum=["true", "false"],
    location="query",
    required=False,
    description="Controls whether to insert the record anyway, even though it may already exist.",
    style="form",
    explode=True,
)


GET_PARAMETERS = [STATS_PARAM, SINCE_PARAM, BEFORE_PARAM]

GET_PARAMETERS_WITHOUT_DATETIME = [
    STATS_PARAM,
    SINCE_PARAM_WITHOUT_DATETIME,
    BEFORE_PARAM_WITHOUT_DATETIME,
]
POST_PARAMETERS = [OVERWRITE_PARAM]

ACTION_PARAM = OpenApiParameter(
    name="action",
    enum=["delete_older_than", "truncate"],
    location="query",
    required=True,
    description="Parameter selecting which delete action to make.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Ex. 1",
            value="delete_older_than",
            summary="Using delete_older_than",
            description="Use `delete_older_than` to delete records older than or equal a date given as the first value in `args`.",
        ),
        OpenApiExample(
            name="Ex. 2",
            value="truncate",
            summary="Using truncate",
            description="Use `truncate` to delete all history.",
        ),
    ],
)

ARGS_PARAM = OpenApiParameter(
    name="args",
    many=True,
    location="query",
    description="All parameters for a delete action.",
    style="form",
    explode=True,
)

DELETE_PARAMS = [ACTION_PARAM, ARGS_PARAM]
