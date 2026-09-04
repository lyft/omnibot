import io
import json
from types import SimpleNamespace

from botocore.exceptions import ClientError

from omnibot.callbacks.network_callbacks import lambda_callback


def _container():
    return SimpleNamespace(
        payload={"text": "hello"},
        event_trace={"event_id": "event-1"},
    )


def test_lambda_callback(mocker):
    callback_response = {"actions": [{"action": "chat.postMessage"}]}
    client = mocker.Mock()
    client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": io.BytesIO(json.dumps(callback_response).encode("utf-8")),
    }
    get_boto_client = mocker.patch(
        "omnibot.callbacks.network_callbacks.get_boto_client",
        return_value=client,
    )
    request_kwargs = {"FunctionName": "eventbot"}

    result = lambda_callback(
        _container(),
        request_kwargs=request_kwargs,
        client_kwargs={"region": "us-east-1"},
    )

    assert result == callback_response
    assert request_kwargs == {"FunctionName": "eventbot"}
    get_boto_client.assert_called_once_with("lambda", region="us-east-1")
    client.invoke.assert_called_once_with(
        FunctionName="eventbot",
        Payload=b'{"text": "hello"}',
    )


def test_lambda_callback_without_request_kwargs(mocker):
    get_boto_client = mocker.patch(
        "omnibot.callbacks.network_callbacks.get_boto_client",
    )

    assert lambda_callback(_container()) == {}
    get_boto_client.assert_not_called()


def test_lambda_callback_handles_invocation_error(mocker):
    client = mocker.Mock()
    client.invoke.side_effect = ClientError(
        {"Error": {"Code": "AccessDeniedException", "Message": "denied"}},
        "Invoke",
    )
    mocker.patch(
        "omnibot.callbacks.network_callbacks.get_boto_client",
        return_value=client,
    )

    assert (
        lambda_callback(
            _container(),
            request_kwargs={"FunctionName": "eventbot"},
        )
        == {}
    )


def test_lambda_callback_handles_function_error(mocker):
    client = mocker.Mock()
    client.invoke.return_value = {
        "StatusCode": 200,
        "FunctionError": "Unhandled",
        "Payload": io.BytesIO(b'{"errorMessage": "failed"}'),
    }
    mocker.patch(
        "omnibot.callbacks.network_callbacks.get_boto_client",
        return_value=client,
    )

    assert (
        lambda_callback(
            _container(),
            request_kwargs={"FunctionName": "eventbot"},
        )
        == {}
    )


def test_lambda_callback_handles_empty_or_invalid_response(mocker):
    client = mocker.Mock()
    mocker.patch(
        "omnibot.callbacks.network_callbacks.get_boto_client",
        return_value=client,
    )

    client.invoke.return_value = {"StatusCode": 202}
    assert (
        lambda_callback(
            _container(),
            request_kwargs={
                "FunctionName": "eventbot",
                "InvocationType": "Event",
            },
        )
        == {}
    )

    client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": io.BytesIO(b"not JSON"),
    }
    assert (
        lambda_callback(
            _container(),
            request_kwargs={"FunctionName": "eventbot"},
        )
        == {}
    )

    client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": io.BytesIO(b"[]"),
    }
    assert (
        lambda_callback(
            _container(),
            request_kwargs={"FunctionName": "eventbot"},
        )
        == {}
    )
