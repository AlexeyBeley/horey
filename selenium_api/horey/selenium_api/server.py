import datetime
from pathlib import Path

from flask import Flask, render_template_string, jsonify, request
import logging
from horey.selenium_api.aucton_api import AuctionAPI

auction_api = AuctionAPI()

# Initialize the Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.route('/')
def echo():
    content_type = request.content_type

    if content_type == 'application/json':
        data = request.json
    elif 'application/x-www-form-urlencoded' in content_type:
        data = request.form
    else:
        data = request.data
    return f"echo reply: {data}"


@app.route('/reports')
def reports():
    return Server.self.load_reports()


@app.route('/auction_event_report')
def auction_event_report():
    """

    :return:
    """

    app.logger.info(f"Serving /auction_event_report {request.data=}, {request=}")

    return Server.self.load_report(request.args.get("id"))


# 4. API Endpoint for Auctions Data
@app.route('/update_info')
def update_info():
    app.logger.info("Serving /update_info")
    return Server.self.update_info(auction_event_id=request.args.get("auction_event_id"),
                                   provider_id=request.args.get("provider_id"))


class Server:
    self = None

    def __init__(self):
        self.html_dir_path = Path(__file__).parent / "html"
        self.reports_html_template_name = "reports_page.html"

    # 2. Main Route ("/")
    # This serves the HTML page defined above

    def load_report(self, auction_event_id):
        data = []

        auction_event_reports = auction_api.generate_auction_event_reports()
        for auction_event_report in auction_event_reports:
            if auction_event_report.str_auction_event_id != auction_event_id:
                continue
            app.logger.info(f"Generating report id {auction_event_report.str_auction_event_id}")
            lots = [lot for lot in auction_event_report.auction_event.lots if lot.current_max is not None]

            lots = [lot for lot in lots if lot.interested]
            if not lots:
                continue

            lots = sorted(lots, key=lambda lot: lot.current_max)
            for i, lot in enumerate(lots):
                data.append({"id": i, "item_name": lot.name, "current_bid": lot.current_max,
                             "link": f'<a href="{lot.url}">link</a>'})
            break

        return jsonify(table_data=data, timestamp=auction_event_report.timestamp_text)

    def update_info(self, auction_event_id=None, provider_id=None):
        if provider_id is not None:
            auction_api.update_info_provider_auction_events(provider_id, asynchronous=True)
            return "Started update_info_provider_auction_events"

        if auction_event_id is not None:
            auction_api.update_info_auction_event(auction_event_id, asynchronous=True)
            return "Started update_info_auction_event"

        raise RuntimeError("No update info destination provided")

    def load_reports(self):
        """
        Load report page.

        <button onclick="fetchData('http://127.0.0.1:8000/auction_event_report?id=19')">31/12</button>
        <button id="reload_19" onclick="updateInfo('http://127.0.0.1:8000/auction_event_reload?id=19')">Update Info</button>
         ||
        <button onclick="fetchData('http://127.0.0.1:8000/auction_event_report?id=4')">02/02</button>
        <button id="reload_4" onclick="updateInfo('http://127.0.0.1:8000/auction_event_reload?id=4')">Update Info</button>


        :return:
        """
        provider_navigation_template = """
         <p style="padding: 15px; color: #777;">STRING_REPLACEMENT_PROVIDER_NAME</p>
         <button onclick="updateProvider('http://127.0.0.1:8000/update_info?provider_id=STRING_REPLACEMENT_PROVIDER_ID')">Update Info</button>
         <hr>
        """

        report_navigation_template = """
        <p style="padding: 15px; color: #777;">STRING_REPLACEMENT_FETCH_DATA_BTN_TXT</p>
        <button onclick="fetchDataAndPopulateElement('http://127.0.0.1:8000/auction_event_report?id=STRING_REPLACEMENT_AUCTION_EVENT_ID', 'table-container', buildAuctionEventReport)">Load</button>
        <button onclick="updateInfo('http://127.0.0.1:8000/update_info?auction_event_id=STRING_REPLACEMENT_AUCTION_EVENT_ID')">Update Info</button>
        <hr>
        """

        reports_navigation = "<table>\n"
        providers_navigation = ""
        known_providers = []
        auction_event_reports = auction_api.generate_auction_event_reports()
        auction_id_btn_text_pairs = []
        for auction_event_report in auction_event_reports:
            for lot in auction_event_report.auction_event.lots:
                if lot.interested:
                    break
            else:
                # no interesting lots
                continue
            auction_id_btn_text_pairs.append((auction_event_report.str_auction_event_id, auction_event_report.fetch_data_button_text))

            if auction_event_report.str_provider_id not in known_providers:
                known_providers.append(auction_event_report.str_provider_id)
                providers_navigation += provider_navigation_template.replace("STRING_REPLACEMENT_PROVIDER_NAME",
                                                                             auction_event_report.provider_name). \
                                            replace("STRING_REPLACEMENT_PROVIDER_ID",
                                                    auction_event_report.str_provider_id) \
                                        + "\n"

        with open(self.html_dir_path / self.reports_html_template_name, encoding="utf-8") as file_handler:
            str_contents = file_handler.read()

        rows = []
        for row_elements_start_position in range(len(auction_id_btn_text_pairs))[0:len(auction_id_btn_text_pairs):4]:
            row = auction_id_btn_text_pairs[row_elements_start_position: row_elements_start_position + 4]
            if row:
                rows.append(row)

        for row in rows:
            str_row = "<tr>\n"
            for auction_event_id, btn_text in row:
                str_row += "<td>\n"
                str_row += report_navigation_template.replace("STRING_REPLACEMENT_AUCTION_EVENT_ID",
                                                                     auction_event_id). \
                                      replace("STRING_REPLACEMENT_FETCH_DATA_BTN_TXT",
                                              btn_text) + "\n"
                str_row += "</td>\n"
            str_row += "</tr>\n"
            reports_navigation += str_row
        reports_navigation += "</table>"

        return str_contents.replace("STRING_REPLACEMENT_REPORTS_NAVIGATION_BUTTONS", reports_navigation).replace(
            "STRING_REPLACEMENT_PROVIDERS_NAVIGATION_BUTTONS", providers_navigation)

    def run(self):
        if Server.self is None:
            Server.self = Server()
            app.logger.info("Starting Flask server on http://127.0.0.1:8000")
            app.run(host='127.0.0.1', port=8000, debug=True)


# 5. Run the application
if __name__ == '__main__':
    server = Server()
    server.run()
