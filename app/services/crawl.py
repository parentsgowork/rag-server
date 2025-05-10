from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def crawl_all_jobs():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")  # 확인 후 주석 해제 가능

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # (준)고령자(50세 이상) 필터가 포함된 URL로 직접 진입
        url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?basicSetupYn=&careerTo=&keywordJobCd=&occupation=&seqNo=&cloDateEndtParam=&payGbn=&templateInfo=&rot2WorkYn=&shsyWorkSecd=&resultCnt=10&keywordJobCont=&cert=&moreButtonYn=Y&minPay=&codeDepth2Info=11000&currentPageNo=1&eventNo=&mode=&major=&resrDutyExcYn=&eodwYn=&sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=&carrEssYns=&benefitSrchAndOr=O&disableEmpHopeGbn=&actServExcYn=&keywordStaAreaNm=&maxPay=&emailApplyYn=&codeDepth1Info=11000&keywordEtcYn=&regDateStdtParam=&publDutyExcYn=&keywordJobCdSeqNo=&viewType=&exJobsCd=&templateDepthNmInfo=&region=&employGbn=&empTpGbcd=1&computerPreferential=&infaYn=&cloDateStdtParam=&siteClcd=all&searchMode=Y&birthFromYY=&indArea=&careerTypes=&subEmpHopeYn=&tlmgYn=&academicGbn=&templateDepthNoInfo=&foriegn=&entryRoute=&mealOfferClcd=&basicSetupYnChk=&station=&holidayGbn=&srcKeyword=&academicGbnoEdu=noEdu&enterPriseGbn=&cloTermSearchGbn=&birthToYY=&keywordWantedTitle=&stationNm=&benefitGbn=&keywordFlag=&notSrcKeyword=&essCertChk=&depth2SelCode=&keywordBusiNm=&preferentialGbn=&rot3WorkYn=&regDateEndtParam=&pfMatterPreferential=B&pageIndex=1&termContractMmcnt=&careerFrom=&laborHrShortYn=#scrollLoc"

        driver.get(url)

        # 공고 테이블 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".list_table tbody tr")
            )
        )

        job_elements = driver.find_elements(By.CSS_SELECTOR, ".list_table tbody tr")
        print(f"[크롤링 대상 tr 수]: {len(job_elements)}")
        results = []

        for job in job_elements:
            try:
                title = job.find_element(By.CSS_SELECTOR, "td.tit a").text.strip()
                region = job.find_element(
                    By.CSS_SELECTOR, "td:nth-of-type(3)"
                ).text.strip()
                work_type = job.find_element(
                    By.CSS_SELECTOR, "td:nth-of-type(4)"
                ).text.strip()
                career = job.find_element(
                    By.CSS_SELECTOR, "td:nth-of-type(5)"
                ).text.strip()
                education = job.find_element(
                    By.CSS_SELECTOR, "td:nth-of-type(6)"
                ).text.strip()

                results.append(
                    {
                        "title": title,
                        "region": region,
                        "work_type": work_type,
                        "career": career,
                        "education": education,
                    }
                )

            except Exception as e:
                print("[공고 1개 파싱 실패]:", e)
                continue

        print(f"[최종 수집된 공고 수]: {len(results)}")
        return results

    finally:
        driver.quit()
