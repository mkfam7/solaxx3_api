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

SINCE_PARAM = lambda upload_date_column: OpenApiParameter(
    name="since",
    type=(OpenApiTypes.DATETIME if upload_date_column.endswith("time") else OpenApiTypes.DATE),
    location="query",
    required=False,
    description="First date in filter range. Optional.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Ex. 1",
            summary="Using a datetime value",
            value="2023-01-01 00:00",
            description="You can use an ISO-8601 format to specify the datetime.",
        ),
        OpenApiExample(
            name="Ex. 2",
            summary="Using a date value",
            value="2023-01-01",
            description="You can also pass an ISO-8601 date instead of datetime.",
        ),
    ],
)

BEFORE_PARAM = lambda upload_date_column: OpenApiParameter(
    name="before",
    type=(OpenApiTypes.DATETIME if upload_date_column.endswith("time") else OpenApiTypes.DATE),
    location="query",
    required=False,
    description="Second date in filter range. Optional.",
    style="form",
    explode=True,
    examples=[
        OpenApiExample(
            name="Ex. 1",
            summary="Using a datetime value",
            value="2023-01-01 00:00",
            description="You can use an ISO-8601 format to specify the datetime.",
        ),
        OpenApiExample(
            name="Ex. 2",
            summary="Using a date value",
            value="2023-01-01",
            description="You can also pass an ISO-8601 date instead of datetime.",
        ),
    ],
)

SINCE_PARAM_WITHOUT_DATETIME = lambda upload_date_column: OpenApiParameter(
    name="since",
    type=(OpenApiTypes.DATETIME if upload_date_column.endswith("time") else OpenApiTypes.DATE),
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

BEFORE_PARAM_WITHOUT_DATETIME = lambda upload_date_column: OpenApiParameter(
    name="before",
    type=(OpenApiTypes.DATETIME if upload_date_column.endswith("time") else OpenApiTypes.DATE),
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


GET_PARAMETERS = lambda upload_date_column: [
    STATS_PARAM,
    SINCE_PARAM(upload_date_column),
    BEFORE_PARAM(upload_date_column),
]

GET_PARAMETERS_WITHOUT_DATETIME = lambda upload_date_column: [
    STATS_PARAM,
    SINCE_PARAM_WITHOUT_DATETIME(upload_date_column),
    BEFORE_PARAM_WITHOUT_DATETIME(upload_date_column),
]
POST_PARAMETERS = [OVERWRITE_PARAM]

MODE_PARAM = OpenApiParameter(
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

DELETE_PARAMS = [MODE_PARAM, ARGS_PARAM]
