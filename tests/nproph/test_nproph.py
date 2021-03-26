from timemachines.skatertools.data.real import hospital_with_exog, hospital
from timemachines.skaters.nproph.nprophskaterfactory import fbnprophet_skater_factory
from timemachines.skatertools.utilities.nonemath import nearlysame
from timemachines.skaters.nproph.nprophiskaterfactory import (
    nprophet_iskater_factory,
    nprophet_fit_and_predict_simple, 
    nprophet_fit_and_predict_with_time,
    nprophet_fit_and_predict_with_time_and_advance_time,
    nprophet_fit_and_predict_with_advance_vars, 
    nprophet_fit_and_predict_with_exog_and_advance_vars,
    nprophet_fit_and_predict_with_exog_and_advance_vars_no_t
)


def test_univariate_without_time(show=False):
    k = 3
    n = 100
    y = hospital(n=n)
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = nprophet_fit_and_predict_simple(y=y, k=k)
    assert nearlysame(x1, x, 0.0001)
    if show:
        m.plot(forecast)
        m1.plot(forecast1)
        import matplotlib.pyplot as plt
        plt.show()


def test_univariate_with_time(show=False):
    k = 3
    n = 100
    y = hospital(n=n)
    t = [i * 15 * 50 for i in range(len(y))]
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, t=t)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = nprophet_fit_and_predict_with_time(y=y, k=k, t=t)
    assert nearlysame(x1, x, 0.0001)
    if show:
        m.plot(forecast)
        m1.plot(forecast1)
        import matplotlib.pyplot as plt
        plt.show()


def test_univariate_with_time_and_advance_time(show=False):
    k = 3
    n = 100
    y = hospital(n=n)
    t = [i * 15 * 50 for i in range(len(y) + k)]
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, t=t)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = nprophet_fit_and_predict_with_time_and_advance_time(y=y, k=k, t=t)
    assert nearlysame(x1, x, 0.0001)
    if show:
        m.plot(forecast)
        m1.plot(forecast1)
        import matplotlib.pyplot as plt
        plt.show()


def test_univariate_with_time_and_advance_vars(show=False):
    k = 3
    n = 100
    y, a = hospital_with_exog(k=k, n=n)
    y1 = [yt[0] for yt in y[:-k]]
    t = [i * 15 * 50 for i in range(len(y1) + k)]
    x, x_std, forecast, m = nprophet_iskater_factory(y=y1, k=k, t=t, a=a)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = nprophet_fit_and_predict_with_advance_vars(y=y1, k=k, t=t, a=a)
    assert nearlysame(x1, x, 0.0001)
    if show:
        m.plot(forecast)
        m1.plot(forecast1)
        import matplotlib.pyplot as plt
        plt.show()


def test_with_exog_and_advance_vars(show=False):
    k = 3
    n = 100
    y, a = hospital_with_exog(k=k, n=n)
    y = y[:-k]
    t = [i * 15 * 50 for i in range(len(y) + k)]
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, t=t, a=a,)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = \
        nprophet_fit_and_predict_with_exog_and_advance_vars(y=y, k=k, t=t, a=a)
    # assert nearlysame(x1, x, 0.0001)
    if show:
        print('forecast', forecast)
        print('forecast1', forecast1)
        m.plot(forecast)
        m1.plot(forecast1)
        m.plot_parameters()
        m1.plot_parameters()
        import matplotlib.pyplot as plt
        plt.show()


def test_with_exog_and_advance_vars_no_t(show=False):
    k = 3
    n = 100
    y, a = hospital_with_exog(k=k, n=n)
    y = y[:-k]
    freq = '15min'
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, freq=freq, a=a)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = nprophet_fit_and_predict_with_exog_and_advance_vars_no_t(y=y, k=k, freq=freq, a=a)
    if not nearlysame(x1, x, 0.0001):
        print(forecast.tail())
        print(forecast1.tail())
        pass
    if show:
        m.plot(forecast)
        m1.plot(forecast1)
        import matplotlib.pyplot as plt
        plt.show()


def test_with_exog_and_advance_vars_no_t_or_freq(show=False):
    k = 3
    n = 600
    y, a = hospital_with_exog(k=k, n=n)
    y = y[:-k]
    freq = None
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, freq=freq, a=a)
    assert len(x) == k
    x1, x_std1, forecast1, m1 = nprophet_fit_and_predict_with_exog_and_advance_vars_no_t(y=y, k=k, freq=freq, a=a)
    if not nearlysame(x1, x, 0.0001):
        print(forecast.tail())
        print(forecast1.tail())
        pass
    if show:
        m.plot(forecast)
        m1.plot(forecast1)
        import matplotlib.pyplot as plt
        plt.show()


def test_with_freq(show=False):
    k = 3
    n = 600
    y, a = hospital_with_exog(k=k, n=n + 2)
    y = y[:n - k]
    a = a[:n]
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, a=a, freq='15min')
    assert len(x) == k
    if show:
        m.plot(forecast)
        import matplotlib.pyplot as plt
        plt.show()


def test_with_freq_recursive(show=False):
    k = 5
    n = 600
    y, a = hospital_with_exog(k=k, n=n + 2, offset=True)
    y = y[:n - k]
    a = a[:n]
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, a=a, freq='15min', recursive=True)
    assert len(x) == k
    if show:
        m.plot(forecast)
        import matplotlib.pyplot as plt
        plt.show()


def test_compare_recursive(show=False):
    k = 5
    n = 800
    y, a = hospital_with_exog(k=k, n=n + 2, offset=True)
    y = y[:n - k]
    a = a[:n]
    assert len(a)==len(y)+k, ' You need smaller n '
    x, x_std, forecast, m = nprophet_iskater_factory(y=y, k=k, a=a, freq='15min', recursive=True)
    x1, x1_std, forecast1, m1 = nprophet_iskater_factory(y=y, k=k, a=a, freq='15min', recursive=False)
    if show:
        m.plot(forecast)
        import matplotlib.pyplot as plt
        plt.title('Using exogenous')
        m1.plot(forecast1)
        plt.title('Not using exogenous')
        print(list(zip(x, x1)))
        plt.show()


def test_skater_with_a():
    k = 3
    y, a = hospital_with_exog(k=k, n=100)
    f1 = fbnprophet_skater_factory
    s1 = {}

    for yt, at in zip(y, a):
        x1, x1_std, s1 = f1(y=yt, s=s1, k=k, a=at)
        if s1.get('m'):
            break  # Stop after first fit


if __name__ == '__main__':
    test_with_exog_and_advance_vars(show=True)
