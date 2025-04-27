import asyncio
import datetime

from PyQt6.QtCharts import QChart, QValueAxis, QChartView, QBarCategoryAxis, QBarSet, QBarSeries, QPieSeries, QPieSlice, \
    QLegend
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from qasync import asyncSlot

from services.supabase.controllers.billing.billing_controller import BillingController
from signals import SignalRepositorySingleton
import pandas as pd
from dateutil import parser

from views.componenets.customsComponents.custom_lable_with_icon import CustomLabelWithIcon


class RevenueAnalyticView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = None
        self.parent = parent
        self.current_month = datetime.datetime.now().month

        self.signals = SignalRepositorySingleton.instance()
        self.parent.year_picker.currentTextChanged.connect(self.update_analytic_based_on_year)


        self.billing_controller = BillingController()

        self.months_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                             "October", "November", "December"]

        # Total Revenue Chart
        self.total_revenue_chart = QChart()
        self.total_revenue_chart_view = QChartView(self.total_revenue_chart)
        self.total_revenue_chart_view.setMinimumSize(400, 400)

        # Payment Methods Chart
        self.payment_methods_chart = QChart()
        self.payment_methods_chart_view = QChartView(self.payment_methods_chart)
        self.payment_methods_chart_view.setMinimumSize(400, 400)

        self.main_layout = QHBoxLayout()

        self.create_total_revenue_chart()
        self.create_payment_methods_chart()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addLayout(self.main_layout)

        self.setLayout(layout)

        asyncio.create_task(self.get_initial_data())

    async def get_initial_data(self):
        self.data = await self.billing_controller.get_all_billings_by_year(
            self.parent.current_year)

    def create_total_revenue_chart(self):

        legend = self.total_revenue_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)


        self.total_revenue_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.total_revenue_chart.setAnimationDuration(1000)
        self.total_revenue_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.main_layout.addWidget(self.total_revenue_chart_view)

    def create_payment_methods_chart(self):

        legend = self.payment_methods_chart.legend()
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setMarkerShape(QLegend.MarkerShape.MarkerShapeCircle)
        legend.setLabelColor(Qt.GlobalColor.darkGray)

        self.payment_methods_chart.setTitle("Payment Methods Distribution")

        self.payment_methods_chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.payment_methods_chart.setAnimationDuration(1000)
        self.payment_methods_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.main_layout.addWidget(self.payment_methods_chart_view)

    def update_total_revenue_chart(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["billing_id", "status", "billing_date", "net_amount"])
            df['billing_date'] = df['billing_date'].apply(parser.parse)
            df['month'] = df['billing_date'].dt.strftime('%B')

            # Filter only paid payments
            df_paid = df[df['status'] == 'paid']

            monthly_data = df_paid.groupby('month').agg(
                total_amount=('net_amount', 'sum')
            ).reset_index()

            monthly_data['month'] = pd.Categorical(monthly_data['month'], categories=self.months_order, ordered=True)
            monthly_data = monthly_data.sort_values('month')

            total_amount_list = []

            for month in self.months_order:
                if month in monthly_data['month'].values:
                    total_amount = monthly_data.loc[monthly_data['month'] == month, 'total_amount'].values[
                        0]
                else:
                    total_amount = 0
                total_amount_list.append(total_amount)

            total_amount_set = QBarSet("Amount")
            total_amount_set.setColor(QColor("#fbbf24"))

            total_amount_set.append(total_amount_list)

            series = QBarSeries()
            series.append(total_amount_set)

            self.total_revenue_chart.removeAllSeries()

            for axis in self.total_revenue_chart.axes():
                self.total_revenue_chart.removeAxis(axis)

            self.total_revenue_chart.addSeries(series)

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)
            self.total_revenue_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axis_x)

            axis_y = QValueAxis()
            self.total_revenue_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axis_y)

            percentage_change_data = calculate_percentage_change(
                total_amount_list[self.current_month - 1],
                total_amount_list[self.current_month - 2]
            )
            self.update_percentage_change_card(percentage_change_data)

        else:
            self.update_percentage_change_card({
                "trend_type": "no change",
                "trend_value": 0,
                "total_revenue": 0
            })

            self.total_revenue_chart.removeAllSeries()

            for axis in self.total_revenue_chart.axes():
                self.total_revenue_chart.removeAxis(axis)

            series = QBarSeries()

            axis_x = QBarCategoryAxis()
            axis_x.append(self.months_order)

            axis_y = QValueAxis()

            self.total_revenue_chart.addSeries(series)

            self.total_revenue_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            self.total_revenue_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

    def update_payment_methods_chart(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["billing_id", "billing_date", "payment_method"])
            df['billing_date'] = df['billing_date'].apply(parser.parse)

            df['month'] = df['billing_date'].dt.strftime('%B')

            payment_methods = df['payment_method'].value_counts()

            total_count = payment_methods.sum()

            self.payment_methods_chart.removeAllSeries()

            series = QPieSeries()

            for method, count in payment_methods.items():
                percentage = QPieSlice(f"{method} {count / total_count:.1%}", count)
                series.append(percentage)


            series.slices()[0].setColor(QColor("#ffcd6a"))
            if len(series.slices()) > 1:
                series.slices()[1].setColor(QColor("#f87171"))

            self.payment_methods_chart.addSeries(series)

        else:
            self.payment_methods_chart.removeAllSeries()

            series = QPieSeries()
            series.append([])
            self.payment_methods_chart.addSeries(series)

    def update_percentage_change_card(self, data):
        self.parent.total_revenue_card.update_data(data)

    @pyqtSlot(str)
    @asyncSlot()
    async def update_analytic_based_on_year(self, year):
        self.data = await self.billing_controller.get_all_billings_by_year(year)
        self.update_total_revenue_chart()
        self.update_payment_methods_chart()


def calculate_percentage_change(current_month, previous_month):
    if current_month:
        if previous_month == 0:
            percentage_change = 0
        else:
            percentage_change = ((
                                         current_month - previous_month) / previous_month) * 100
        trend_type = "increased" if percentage_change > 0 else "decreased"
        return {
            "trend_type": trend_type,
            "trend_value": abs(int(percentage_change)),
            "total_revenue": current_month
        }
    return {
        "trend_type": "no change",
        "trend_value": 0,
        "total_revenue": current_month
    }


class TotalRevenueCard(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)

        revenue_label = CustomLabelWithIcon(name="Revenue",
                                            icon_path=":resources/icons/revenue_analytic.svg",
                                            icon_size=QSize(25, 25))

        revenue_label.label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#24282B;
                  font-size:12pt;
                  padding-left:5px;
              }
        """)

        self.total_revenue_label = QLabel("$" + str(data["total_revenue"]))
        self.total_revenue_label.setMinimumHeight(30)
        self.total_revenue_label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#24282B;
                  font-size:16pt;
                  padding-left:5px;
              }
        """)

        top_central_widget = QWidget()
        top_central_widget.setStyleSheet("border:1px solid #DCE6EB;border-radius:15px;background-color:white;")

        top_central_layout = QVBoxLayout(top_central_widget)
        top_central_layout.setSpacing(20)
        top_central_layout.setContentsMargins(15, 15, 15, 15)

        top_central_layout.addWidget(revenue_label)
        top_central_layout.addWidget(self.total_revenue_label)

        if data["trend_type"] == "increased":
            self.trend_label = CustomLabelWithIcon(name=str(int(data["trend_value"])) + "%",
                                                   icon_path=":resources/icons/trend_up.svg",
                                                   icon_size=QSize(15, 15))
            self.trend_label.label.setStyleSheet("""
                       border:0;
                       background-color:transparent;
                       color:#2db5cd;
                       font-size:8pt;
             """)
        else:
            self.trend_label = CustomLabelWithIcon(name=str(int(data["trend_value"])) + "%",
                                                   icon_path=":resources/icons/trend_down.svg",
                                                   icon_size=QSize(15, 15))
            self.trend_label.label.setStyleSheet("""
                           border:0;
                           background-color:transparent;
                           color:#D02048;
                           font-size:8pt;

                 """)

        compare_to_last_month_label = QLabel("Compare to last month")
        compare_to_last_month_label.setStyleSheet("""
         QLabel {
                  border:0;
                  background-color:transparent;
                  color:#848484;
                  font-size:8pt;
              }
        """)

        trending_layout = QHBoxLayout()
        trending_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        trending_layout.setContentsMargins(15, 0, 15, 0)
        trending_layout.setSpacing(20)

        trending_layout.addWidget(self.trend_label, Qt.AlignmentFlag.AlignLeft)
        trending_layout.addWidget(compare_to_last_month_label, Qt.AlignmentFlag.AlignRight)

        lower_central_widget = QWidget()
        lower_central_widget.setStyleSheet("""
            border:0;
            border-left:1px solid #DCE6EB;
            border-right:1px solid #DCE6EB;
            border-bottom:1px solid #DCE6EB;
            border-radius:15px;
            background-color:#f9f9f9;
        """)

        lower_central_layout = QVBoxLayout(lower_central_widget)
        lower_central_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        lower_central_layout.setContentsMargins(0, 0, 0, 10)

        lower_central_layout.addWidget(top_central_widget)

        lower_central_layout.addLayout(trending_layout)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(lower_central_widget)

        self.setFixedSize(235, 140)

        self.setLayout(layout)

    def update_data(self, data):
        self.total_revenue_label.setText("$" + str(data["total_revenue"]))

        if data["trend_type"] == "increased":
            self.trend_label.label.setText(str(int(data["trend_value"])) + "%")
            self.trend_label.label.setStyleSheet("""
                        border:0;
                        background-color:transparent;
                        color:#2db5cd;
                       font-size:10pt;
              """)
            pixmap = QPixmap(":resources/icons/trend_up.svg").scaled(15, 15)
            self.trend_label.icon_label.setPixmap(pixmap)
        else:
            self.trend_label.label.setText(str(data["trend_value"]) + "%")
            self.trend_label.label.setStyleSheet("""
                            border:0;
                            background-color:transparent;
                            color:#D02048;
                           font-size:10pt;
              """)
            pixmap = QPixmap(":resources/icons/trend_down.svg").scaled(15, 15)
            self.trend_label.icon_label.setPixmap(pixmap)
