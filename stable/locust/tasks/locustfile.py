from locust import HttpLocust, TaskSet, task
import logging
import sys
import time
USER_PANELS = [
    ("SINGLE0001", "LASER"),
]
USED_UNITS = []


class UserTasks(TaskSet):

    def on_start(self):
        logging.info("Running on_start")

    def teardown(self):
        logging.info("Running on_end")

        for unit in USED_UNITS:
            panelid, equipment = unit.pop()
            endpoint = "/v1.0/equipments/{}/units/{},TRACE_ID".format(
                equipment, panelid)
            logging.info("Reseting unit {}".format(panelid))
            self.client.patch(
                endpoint, """{"data": {"unitStatus": "checkin"}}""")
            self.client.patch(
                endpoint, """{"data": {"unitStatus": "checkout","unitResult": "PASS"}}""")

    @task
    def task1(self):
        if len(USER_PANELS) > 0:
            self.panelid, self.equipment = USER_PANELS.pop()
            if [(self.panelid, self.equipment)] not in USED_UNITS:
                USED_UNITS.append([(self.panelid, self.equipment)])
            logging.info("Nuber of used units: {}".format(len(USED_UNITS)))
        else:
            logging.info("No more units available. Recreating units")
            self.panelid = "NOT_FOUND"
            self.equipment = "NOT_FOUND"
        logging.info("Running task")
        logging.info(
            "Running equipment identification {}".format(self.panelid))
        endpoint1 = "/v1.0/equipments/{}".format(self.equipment)
        logging.info("Issuing: GET {}".format(endpoint1))
        self.client.get(endpoint1)
        time.sleep(0.2)
        logging.info("Running unit checkin {}".format(self.panelid))
        endpoint = "/v1.0/equipments/{}/units/{},FE_PANEL".format(
            self.equipment, self.panelid)
        logging.info("Issuing: PATCH (checkin) {}".format(endpoint))
        self.client.patch(endpoint, """{"data": {"unitStatus": "checkin"}}""")
        time.sleep(2.0)
        logging.info("Running unit checkout {}".format(self.panelid))
        logging.info("Issuing: PATCH (checkout) {}".format(endpoint))
        self.client.patch(
            endpoint, """{"data": {"unitStatus": "checkout","unitResult": "PASS"}}""")
        USER_PANELS.append([self.panelid, self.equipment])
        logging.info("Unit released {}".format(self.panelid))


class WebsiteUser(HttpLocust):
    task_set = UserTasks
    min_wait = 100
    max_wait = 200
