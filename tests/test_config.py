def test_get_default_device_cuda(mocker):
    # Mock torch.cuda.is_available to return True
    mock_torch = mocker.Mock()
    mock_torch.cuda.is_available.return_value = True
    mocker.patch.dict("sys.modules", {"torch": mock_torch})
    
    # We need to re-import or use the function if it's exported
    from src.config import get_default_device
    assert get_default_device() == "cuda"

def test_get_default_device_cpu(mocker):
    # Mock torch.cuda.is_available to return False
    mock_torch = mocker.Mock()
    mock_torch.cuda.is_available.return_value = False
    mocker.patch.dict("sys.modules", {"torch": mock_torch})
    
    from src.config import get_default_device
    assert get_default_device() == "cpu"

def test_get_default_device_no_torch(mocker):
    # Mock torch to be missing
    mocker.patch.dict("sys.modules", {"torch": None})
    
    from src.config import get_default_device
    assert get_default_device() == "cpu"
