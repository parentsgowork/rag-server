from pydantic import BaseModel


class JobRecommendation(BaseModel):
    jo_reqst_no: str
    jo_regist_no: str
    company_name: str
    job_title: str
    description: str
    deadline: str
    location: str
    pay: str
    registration_date: str
    time: str
