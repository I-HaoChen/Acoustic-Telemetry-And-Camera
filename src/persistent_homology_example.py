import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from src.utils.project_constants import ProjectConstants


def plot_superlevel_set_example():
    fig = make_subplots(
        rows=2,
        cols=4,
        row_heights=[0.4, 0.6],
        specs=[
            [{}, {}, {}, {}],
            [{"colspan": 3}, None, None, {}]
        ],
        shared_yaxes=False, shared_xaxes=False,
        subplot_titles=(
            r"$\text{(A) } c = 3$", r"$\text{(B) }c = 2$", r"$\text{(C) } c = 1$", r"$\text{(D) }c = 0.5$",
            r"$\text{(E) Persistent Peaks}$", r"$\text{(F) } 0\text{-th Dim. Pers. Diagram}$", None, None)
    )

    x_data = [1, 2, 3, 4]
    y_data = [0.5, 2, 1, 3]
    trace = go.Scatter(x=[1, 2, 3, 4], y=y_data, mode='lines+markers',
                       marker=dict(color=px.colors.qualitative.Dark2[0]),
                       showlegend=False, legendgroup="1")
    for i in range(1, 5):
        fig.add_trace(trace, row=1, col=i)
        fig.update_xaxes(range=[0, 4.5], row=1, col=i)
        fig.update_yaxes(range=[0, 4], row=1, col=i)

        fig.add_shape(
            type="line",
            x0=0, x1=4, y0=3, y1=3,
            line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
            xref=f'x{i}', yref=f'y{i}'
        )

    for i in range(2, 5):
        fig.add_shape(
            type="line",
            x0=0, x1=4, y0=2, y1=2,
            line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
            xref=f'x{i}', yref=f'y{i}'
        )

    for i in range(3, 5):
        fig.add_shape(
            type="line",
            x0=0, x1=4, y0=1, y1=1,
            line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
            xref=f'x{i}', yref=f'y{i}'
        )

    for i in range(4, 5):
        fig.add_shape(
            type="line",
            x0=0, x1=4, y0=0.5, y1=0.5,
            line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
            xref=f'x{i}', yref=f'y{i}'
        )

    # Sinking water levels
    fig.add_shape(
        type="rect",
        x0=0, x1=4.5, y0=0, y1=3,
        fillcolor=px.colors.qualitative.Pastel1[1], opacity=0.5,
        line=dict(width=0),
        xref=f'x1', yref=f'y1'
    )
    fig.add_shape(
        type="rect",
        x0=0, x1=4.5, y0=0, y1=2,
        fillcolor=px.colors.qualitative.Pastel1[1], opacity=0.5,
        line=dict(width=0),
        xref=f'x2', yref=f'y2'
    )
    fig.add_shape(
        type="rect",
        x0=0, x1=4.5, y0=0, y1=1,
        fillcolor=px.colors.qualitative.Pastel1[1], opacity=0.5,
        line=dict(width=0),
        xref=f'x3', yref=f'y3'
    )
    fig.add_shape(
        type="rect",
        x0=0, x1=4.5, y0=0, y1=0.5,
        fillcolor=px.colors.qualitative.Pastel1[1], opacity=0.5,
        line=dict(width=0),
        xref=f'x4', yref=f'y4'
    )

    # plot 1,1
    fig.add_trace(go.Scatter(x=[4], y=[0.1], mode='lines+markers', line=dict(color=px.colors.qualitative.T10[7]),
                             showlegend=False, legendgroup="1"), row=1, col=1)
    fig.add_shape(
        type="line",
        x0=4, x1=4, y0=0, y1=3,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{1}', yref=f'y{1}'
    )
    fig.add_trace(go.Scatter(x=[0.1], y=[3], mode='lines+markers', line=dict(color=px.colors.qualitative.T10[5]),
                             showlegend=False, legendgroup="1"), row=1, col=1)

    # plot 1,2
    fig.add_trace(go.Scatter(x=[2], y=[0.1], mode='lines+markers', line=dict(color=px.colors.qualitative.T10[7]),
                             showlegend=False, legendgroup="1"), row=1, col=2)
    fig.add_shape(
        type="line",
        x0=4 - (1 / 2), x1=4, y0=0.1, y1=0.1,
        line=dict(color=px.colors.qualitative.T10[7], width=2),
        xref=f'x{2}', yref=f'y{2}',
    )
    fig.add_shape(
        type="line",
        x0=4, x1=4, y0=0, y1=3,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{1}', yref=f'y{1}'
    )
    fig.add_shape(
        type="line",
        x0=4 - (1 / 2), x1=4 - (1 / 2), y0=0, y1=2,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{2}', yref=f'y{2}'
    )
    fig.add_shape(
        type="line",
        x0=2, x1=2, y0=0, y1=2,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{2}', yref=f'y{2}'
    )
    fig.add_shape(
        type="line",
        x0=4, x1=4, y0=0, y1=3,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{2}', yref=f'y{2}'
    )
    fig.add_trace(go.Scatter(x=[0.2], y=[2], mode='lines+markers', line=dict(color=px.colors.qualitative.T10[5]),
                             showlegend=False, legendgroup="1"), row=1, col=2)
    fig.add_shape(
        type="line",
        x0=0.1, x1=0.1, y0=2, y1=3,
        line=dict(color=px.colors.qualitative.T10[5], width=2),
        xref=f'x{2}', yref=f'y{2}',
    )

    # plot 1,3
    fig.add_shape(
        type="line",
        x0=2 - (1 / 1.5), x1=4, y0=0.1, y1=0.1,
        line=dict(color=px.colors.qualitative.T10[7], width=2),
        xref=f'x{3}', yref=f'y{3}',
    )
    fig.add_shape(
        type="line",
        x0=4, x1=4, y0=0, y1=3,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{3}', yref=f'y{3}',
    )
    fig.add_shape(
        type="line",
        x0=2 - (1 / 1.5), x1=2 - (1 / 1.5), y0=0, y1=1,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{3}', yref=f'y{3}',
    )
    fig.add_shape(
        type="line",
        x0=0.1, x1=0.1, y0=1, y1=3,
        line=dict(color=px.colors.qualitative.T10[5], width=2),
        xref=f'x{3}', yref=f'y{3}',
    )
    fig.add_shape(
        type="line",
        x0=0.2, x1=0.2, y0=1, y1=2,
        line=dict(color=px.colors.qualitative.T10[5], width=2),
        xref=f'x{3}', yref=f'y{3}',
    )
    fig.add_trace(go.Scatter(x=[x_data[1]], y=[y_data[1]], mode='markers', showlegend=False,
                             legendgrouptitle_text="Persistent Peaks",
                             marker=dict(size=10, color=ProjectConstants.COLOR_LIST_PEAKS[1]),
                             ), row=1, col=3)
    # plot 1,4
    fig.add_shape(
        type="line",
        x0=1, x1=4, y0=0.1, y1=0.1,
        line=dict(color=px.colors.qualitative.T10[7], width=2),
        xref=f'x{4}', yref=f'y{4}',
    )
    fig.add_shape(
        type="line",
        x0=4, x1=4, y0=0, y1=3,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{4}', yref=f'y{4}',
    )
    fig.add_shape(
        type="line",
        x0=1, x1=1, y0=0, y1=0.5,
        line=dict(color=px.colors.qualitative.Set1[0], width=2, dash='dot'),
        xref=f'x{4}', yref=f'y{4}',
    )

    fig.add_shape(
        type="line",
        x0=0.2, x1=0.2, y0=1, y1=2,
        line=dict(color=px.colors.qualitative.T10[5], width=2),
        xref=f'x{4}', yref=f'y{4}',
    )
    fig.add_shape(
        type="line",
        x0=0.1, x1=0.1, y0=0.5, y1=3,
        line=dict(color=px.colors.qualitative.T10[5], width=2),
        xref=f'x{4}', yref=f'y{4}',
    )

    fig.add_trace(go.Scatter(x=[x_data[3]], y=[y_data[3]], mode='markers', showlegend=False,
                             marker=dict(size=10, color=ProjectConstants.COLOR_LIST_PEAKS[0]),
                             ), row=1, col=4)
    fig.add_trace(go.Scatter(x=[x_data[1]], y=[y_data[1]], mode='markers', showlegend=False,
                             legendgrouptitle_text="Persistent Peaks",
                             marker=dict(size=10, color=ProjectConstants.COLOR_LIST_PEAKS[1]),
                             ), row=1, col=4)
    # plot 2,1
    fig.add_trace(
        go.Scatter(x=x_data, y=y_data, mode='lines+markers', marker=dict(color=px.colors.qualitative.Dark2[0]),
                   showlegend=False),
        row=2, col=1)

    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        # name=r"$(a_i)_{i \in \{1\dots 4\}$",
        name=r"Time Series",
        marker_color=px.colors.qualitative.Dark2[0],
        mode='lines',
        legendgroup="general",
        legendgrouptitle_text="General"))

    fig.add_shape(type="line", x0=2, x1=2, y0=1, y1=2,
                  line=dict(color=px.colors.qualitative.T10[5], width=1.5), row=2,
                  col=1)
    fig.add_shape(type="line", x0=4, x1=4, y0=0.5, y1=3,
                  line=dict(color=px.colors.qualitative.T10[5], width=1.5),
                  row=2, col=1)

    fig.add_trace(go.Scatter(x=[x_data[3]], y=[y_data[3]], mode='markers', legendgroup="Persistence", name="Peak 1",
                             marker=dict(size=10, color=ProjectConstants.COLOR_LIST_PEAKS[0]),
                             ), row=2, col=1)
    fig.add_trace(go.Scatter(x=[x_data[1]], y=[y_data[1]], mode='markers', legendgroup="Persistence", name="Peak 2",
                             legendgrouptitle_text="Persistent Peaks",
                             marker=dict(size=10, color=ProjectConstants.COLOR_LIST_PEAKS[1]),
                             ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        name="Persistence",
        marker_color=px.colors.qualitative.T10[5],
        mode='lines',
        legendgroup="Persistence"))
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        name="Connected Components",
        marker_color=px.colors.qualitative.T10[7],
        mode='lines',
        legendgroup="Persistence"))

    fig.update_xaxes(range=[0, 4.5], row=2, col=1)
    fig.update_yaxes(range=[0, 4], row=2, col=1)

    # plot 2,2
    fig.add_trace(
        go.Scatter(x=[4, 0, 0], y=[4, 0, 4], mode='lines', showlegend=False, fill="toself",
                   marker=dict(color=px.colors.qualitative.Dark2[-1]), opacity=0.5), row=2, col=4)
    fig.add_trace(
        go.Scatter(x=[3], y=[0.5], mode='markers', legendgroup="Persistence",
                   name="peak 1",
                   marker=dict(size=10, color=ProjectConstants.COLOR_LIST_PEAKS[0]), showlegend=False), row=2, col=4)
    fig.add_trace(
        go.Scatter(x=[2], y=[1], mode='markers', legendgroup="Persistence", name="peak 2",
                   marker=dict(size=10, color=ProjectConstants.COLOR_LIST_PEAKS[1]), showlegend=False), row=2, col=4)
    fig.update_xaxes(matches=None, row=2, col=4)
    fig.update_yaxes(matches=None, row=2, col=4)
    fig.update_xaxes(range=[4.2, 0], title_text="Birth Level", title_standoff=5, row=2, col=4)
    fig.update_yaxes(range=[4, 0], title_text="Death Level", title_standoff=0, row=2, col=4)
    fig.update_annotations(yshift=10)

    # rest
    annotations = fig.layout.annotations
    for i in range(len(annotations)):
        annotations[i]['y'] += 0.01
    fig.update_layout(legend=dict(x=0.01, y=0.65, borderwidth=1, xanchor="left", yanchor="top"))

    fig.update_layout(width=900, height=450)
    fig.update_layout(title_x=0.5)
    fig.update_layout(go.Layout(margin=go.layout.Margin(l=55, r=55, b=55, t=70)))
    fig.update_layout(template="plotly_white")
    fig.write_image(
        ProjectConstants.PLOTS.joinpath(f"figure_3").with_suffix(".pdf").as_posix())
    fig.show()
