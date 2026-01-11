from screener.filters.st_filters import check_st


def test_st_filter_detects_name():
    result = check_st("*ST测试", [], ["ST", "*ST"])
    assert result.is_filtered is True
