from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict

import sqlite3

router_4 = APIRouter()


##########################################################
@router_4.on_event("shutdown")
@router_4.on_event("startup")
def make_connection():
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    if hasattr('router_4', 'conn'):
        router_4.conn.close()
        print("connection closed")
    else:
        router_4.conn = sqlite3.connect('northwind.db', check_same_thread=False)
        router_4.conn.text_factory = lambda b: b.decode(errors="ignore").strip()
        router_4.conn.row_factory = dict_factory
        print("connection created")


router_4.sql_dict = dict()


####
def extract_end_point_from_request(request: Request):
    my_url = request.url.path[1::].lower()
    try:
        my_url = my_url[0:my_url.index("/"):]
    except ValueError:
        pass
    finally:
        return my_url


def extract_sql_from_endpoint(end_point: str):
    sql = router_4.sql_dict[end_point]
    return sql


def extract_data_from_endpoint(request: Request,
                               QueryParamDict: Optional[Dict] = None,
                               sql: Optional[str] = None,
                               end_point: Optional[str] = None):
    end_point = end_point or extract_end_point_from_request(request)
    sql = sql or extract_sql_from_endpoint(end_point)
    QueryParamDict = QueryParamDict or dict()
    print('type(sql): ', type(sql), " sql: ", sql, ", end_point: ", end_point, ", QueryParamDict: ", QueryParamDict)

    rows = router_4.conn.execute(sql, QueryParamDict).fetchall()

    return sql, end_point, rows


# router_4.sql_dict["4"]="select
#                             P.ProductID id, p.ProductName name,c.CategoryName category,
#                             S.CompanyName supplier
#                         FROM
#                         Products P
#                         left join Suppliers S using(SupplierID)
#                         left join Categories C using(CategoryID)
#                         order by id"


# Na pierwszy ogie?? stw??rz dwa endpointy /categories oraz /customers. Oba endpointy maj?? by?? obs??ugiwane przez metod??
# GET, zwraca?? kod HTTP 200 oraz dane maj?? by?? posortowane po kolumnie id. Endpoint /categories ma zwraca?? rekordy z
# tabeli Categories w nast??puj??cym formacie:
#
# {
#     "categories": [
#          {"id": 1, "name": "Beverages"},
#          [...]
#      ]
# }
# gdzie id to jest kolumna CategoryID, za?? name to CategoryName.
# Endpoint /customers ma zwraca?? rekordy z tabeli Customers w nast??puj??cym formacie:
# {
#     "customers": [
#         {
#             "id": "ALFKI",
#             "name": "Alfreds Futterkiste",
#             "full_address":  "Obere Str. 57 12209 Berlin Germany",
#         },
#         [...]
#      ]
# }
# gdzie id to jest kolumna CustomerID, name to kolumna CompanyName,
# za?? full_address to s?? dane po????czone z czterech kolumn w kolejno??ci:
# Address, PostalCode, City oraz Country oddzielone spacj??.
router_4.sql_dict["categories"] = \
    "SELECT	CategoryID id,CategoryName name " \
    "FROM Categories order by id;"
router_4.sql_dict["customers"] = \
    'SELECT ' \
    'CustomerID id, CompanyName name, Address || " " || PostalCode || " " || City || " " || Country full_address ' \
    'FROM Customers order by id'


@router_4.get("/categories")
@router_4.get("/customers")
def main(request: Request):
    sql, end_point, rows = extract_data_from_endpoint(request)
    response = {end_point: rows}
    return JSONResponse(response)


# ############################### 4.2 Stw??rz kolejny endpoint /products/[id]. Endpoint ma by?? obs??ugiwany przez
# metod?? GET. Ma przyjmowa?? id oraz zwraca?? dane rekordu z tabeli Products pod podanym id. Endpoint standardowo ma
# zwraca?? kod HTTP 200 lub HTTP 404 gdy rekord o podanym id nie istnieje. Zwr??cona odpowied?? ma by?? jsonem w
# nast??puj??cym formacie:
#
# {"id": 1, "name": "Chai"}
# gdzie id to jest kolumna ProductID, za?? name to ProductName.

router_4.sql_dict["products"] = \
    "SELECT ProductID id, ProductName name " \
    "FROM Products where ProductID=:ProductID"


@router_4.get("/products/{id}")
def main(id: int, request: Request):
    QryParamDict = {"ProductID": id}
    sql, end_point, rows = extract_data_from_endpoint(request=request, QueryParamDict=QryParamDict)

    if not len(rows):
        raise HTTPException(404, "ID does not exist")
    return JSONResponse(*rows, status_code=200)


################################ 4.3
# Stw??rz endpoint /employees, obs??ugiwany przez metod?? GET, ma zwraca?? defaultowo kod HTTP 200
# oraz ma pobiera?? dane z tabeli Employees. Dane defaultowo maj?? by?? posortowane po kolumnie id.
# Ponad to endpoint ma obs??ugiwa?? query parametry: limit, offset oraz order.
# Parametry limit oraz offset b??d?? intami, za?? order b??dzie stringiem z nazw?? kolumny po kt??rej
# nale??y posortowa?? dane rosn??co. Dopuszczalne warto??ci dla parametru order to first_name, last_name, city.
# Gdyby parametr order mia?? inn?? warto????, nale??y zwr??ci?? kod HTTP 400.
# Dane z ednpointu maj?? by?? zwr??cone w postaci jsona w nast??puj??cym formacie:
#
# {
#     "employees": [
#         {"id":1,"last_name":"Davolio","first_name":"Nancy","city":"Seattle"},
#         [...]
#    ]
# }
# gdzie id to jest kolumna EmployeeID, last_name to LastName, first_name to FirstName, za?? city to City.
router_4.sql_dict["employees"] = \
    "select " \
    "   EmployeeID id, LastName last_name, FirstName first_name, City city " \
    "from Employees " \
    "order by :_order ASC " \
    "limit :limit " \
    "offset :offset ;"


@router_4.get("/employees", status_code=200)
def main(request: Request,
         limit: int,
         offset: int,
         order: Optional[str] = None):

    # __order_dict={
    #     "id":"EmployeeID",
    #     "last_name":"LastName",
    #     "first_name":"FirstName",
    #     "city":"City"}

    if order not in {'first_name', 'last_name', 'city', None}:
        raise HTTPException(status_code=400, detail='order {} is not recognized'.format(order))
    order=order or 'id'
    # order=__order_dict[order]
    QryParamDict = {"limit": limit, "offset": offset, "_order": order}
    sql, end_point, rows = extract_data_from_endpoint(request=request, QueryParamDict=QryParamDict)

    response = {end_point: rows}
    return JSONResponse(response)


# 4.4
# Stw??rz endpoint /products_extended, obs??ugiwany przez metod?? GET, ma zwraca?? kod HTTP 200
# oraz ma pobiera?? dane z tabeli Products. Dane maj?? by?? posortowane po kolumnie id
# oraz zwr??cone w postaci jsona, w nast??pujacym formacie:
# {
#    "products_extended": [
#        {
#            "id": 1,
#            "name": "Chai",
#            "category": "Beverages",
#            "supplier": "Exotic Liquids",
#        },
#        [...]
#   ]
# }
# gdzie id to  kolumna ProductID, name to ProductName, category to referencja do tabeli Categories i warto???? z kolumny CategoryName, za?? supplier to referencja do tabeli Suppliers i warto???? z kolumny CompanyName.
router_4.sql_dict["products_extended"] = \
    "select P.ProductID id, p.ProductName name, c.CategoryName category, " \
    "S.CompanyName supplier " \
    "FROM Products P " \
    "join Suppliers S using(SupplierID) " \
    "join Categories C using(CategoryID) " \
    "order by P.ProductID"


@router_4.get("/products_extended", status_code=200)
def main(request: Request):
    sql, end_point, rows = extract_data_from_endpoint(request=request)
    response = {end_point: rows}
    return JSONResponse(response)


# 4.5
router_4.sql_dict["products_orders"] = "select " \
    "o.OrderID id, C.CompanyName customer, od.Quantity quantity, " \
    "round( (od.UnitPrice * od.Quantity) - od.Discount * (od.UnitPrice * od.Quantity),2) total_price " \
    "from Orders O " \
    "join Customers C using(CustomerID) " \
    "join 'Order Details' OD using(OrderID) " \
    "where OD.ProductID=:ProductID " \
    "order by o.OrderID ASC"


@router_4.get("/products/{id}/orders", status_code=200)
def main(id: int, request: Request):
    sql, end_point, rows = \
        extract_data_from_endpoint(request=request,
                                   QueryParamDict={"ProductID": id},
                                   end_point='products_orders')

    if not len(rows):
        raise HTTPException(404, "ID does not exist")

    response = {"orders": rows}
    return JSONResponse(response)
