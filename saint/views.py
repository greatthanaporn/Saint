from django.contrib.auth import login
from .models import OTP, User
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.timezone import now
from django.shortcuts import render, redirect
from .models import Flour, Filling, Topping, Sauce,Order,OrderGroup
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group


#-----------------------view สำหรับการกรอกอีเมล

def request_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user, created = User.objects.get_or_create(username=email, email=email)

        # ตรวจสอบว่าผู้ใช้ถูกเพิ่มเข้ากลุ่ม member หรือไม่
        member_group, _ = Group.objects.get_or_create(name="member")
        if not user.groups.filter(name="member").exists():
            user.groups.add(member_group)
            user.save()  # บันทึกการเปลี่ยนแปลง

        otp_code = OTP.generate_otp()
        OTP.objects.create(user=user, otp_code=otp_code)

        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp_code}",
            "your_email@gmail.com",
            [email],
            fail_silently=False,
        )

        request.session["email"] = email
        return redirect("verify_otp")

    return render(request, "request_otp.html")




def verify_otp(request):
    if request.method == "POST":
        email = request.session.get("email")
        otp_input = request.POST.get("otp")

        try:
            user = User.objects.filter(email=email).first()  # ใช้ first() ป้องกัน error หลาย user
            otp = OTP.objects.filter(user=user).latest("created_at")

            if otp.is_valid() and otp.otp_code == otp_input:
                login(request, user)

                # ตรวจสอบ Group และเปลี่ยนเส้นทางตามสิทธิ์
                if user.groups.filter(name="admin").exists():
                    return redirect("Dashboard")
                elif user.groups.filter(name="member").exists():
                    return redirect("order_crepe")
                else:
                    return render(request, "verify_otp.html", {"error": "บัญชีของคุณไม่ได้อยู่ในกลุ่มที่กำหนด"})

            else:
                return render(request, "verify_otp.html", {"error": "OTP ไม่ถูกต้องหรือหมดอายุ"})

        except (User.DoesNotExist, OTP.DoesNotExist):
            return render(request, "verify_otp.html", {"error": "ไม่พบ OTP หรือบัญชีนี้"})

    return render(request, "verify_otp.html")


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse




def accept_order(request, queue_number):
    """ แอดมินกดรับออเดอร์ เปลี่ยนสถานะเป็น 'order_received' """
    if request.method == "POST":
        group = get_object_or_404(OrderGroup, queue_number=queue_number)
        group.status = "order_received"
        group.save()

        # ส่งอีเมลแจ้งเตือนผู้ใช้
        user_email = group.user.email if group.user else None
        if user_email:
            send_mail(
                "ออเดอร์ของคุณได้รับการยืนยันแล้ว",
                f"คิวที่ {queue_number} ออเดอร์ของคุณได้รับการรับแล้ว กำลังเตรียมทำเครป",
                settings.EMAIL_HOST_USER,
                [user_email],
                fail_silently=False,
            )

        return JsonResponse({
            "status": "success",
            "queue_number": queue_number,
            "new_status": "order_received",
            "status_display": "รับออเดอร์แล้ว"
        })
    return JsonResponse({"status": "error", "message": "Method Not Allowed"}, status=405)


def complete_order(request, queue_number):
    """ แอดมินกดออเดอร์เสร็จสิ้น เปลี่ยนสถานะเป็น 'completed' """
    if request.method == "POST":
        group = get_object_or_404(OrderGroup, queue_number=queue_number)
        group.status = "completed"
        group.save()

        # ส่งอีเมลแจ้งเตือนผู้ใช้
        user_email = group.user.email if group.user else None
        if user_email:
            send_mail(
                "เครปของคุณเสร็จแล้ว!",
                f"คิวที่ {queue_number} เครปของคุณเสร็จแล้ว กรุณามาชำระเงิน",
                settings.EMAIL_HOST_USER,
                [user_email],
                fail_silently=False,
            )

        return JsonResponse({"status": "success", "next_action": "mark_paid"})
    return JsonResponse({"status": "error", "message": "Method Not Allowed"}, status=405)



def mark_as_paid(request, queue_number):
    """ แอดมินกดชำระเงินเสร็จสิ้น ไม่ลบจากฐานข้อมูลแต่ซ่อนจากหน้าหลัก """
    if request.method == "POST":
        group = get_object_or_404(OrderGroup, queue_number=queue_number)
        group.status = "paid"
        group.save()

        # ส่งอีเมลขอบคุณลูกค้า
        user_email = group.user.email if group.user else None
        if user_email:
            send_mail(
                "ขอบคุณที่ใช้บริการ!",
                f"ขอบคุณที่สั่งเครปจากร้านของเรา คิวที่ {queue_number} ได้รับการชำระเงินแล้ว หวังว่าจะได้ให้บริการอีกครั้ง!",
                settings.EMAIL_HOST_USER,
                [user_email],
                fail_silently=False,
            )

        return JsonResponse({"status": "success", "next_action": "hide"})
    return JsonResponse({"status": "error", "message": "Method Not Allowed"}, status=405)



#------------------------- View สำหรับตรวจสอบ OTP

def order_crepe(request):
    flours = Flour.objects.all()
    fillings = Filling.objects.all()
    toppings = Topping.objects.all()
    sauces = Sauce.objects.all()

    return render(request, 'order_crepe.html', {
        "flours": flours,
        "fillings": fillings,
        "toppings": toppings,
        "sauces": sauces
    })

def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            if not data.get("flour"):
                return JsonResponse({"status": "error", "message": "กรุณาเลือกแป้งก่อน"}, status=400)

            total_price = data.get("total_price", 0)
            quantity = data.get("quantity", 1)

            # ✅ เพิ่ม user=request.user
            order = Order.objects.create(
                user=request.user,  # ✅ บันทึกผู้ใช้ที่สั่ง
                flour=json.dumps(data["flour"]),
                filling=json.dumps(data.get("fillings", [])),
                topping=json.dumps(data.get("toppings", [])),
                sauce=json.dumps(data.get("sauces", [])),
                total_price=total_price,
                quantity=quantity,
                note=data.get("note", "")
            )

            return JsonResponse({"status": "success", "order_id": order.id, "total_price": total_price})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "JSON ไม่ถูกต้อง"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Method Not Allowed"}, status=405)

def cart(request):
    # ✅ ดึงเฉพาะคำสั่งซื้อที่ยังไม่มี OrderGroup (ยังไม่ได้ยืนยัน)
    pending_orders = Order.objects.filter(order_group__isnull=True).order_by("created_at")
    flours = Flour.objects.all()
    fillings = Filling.objects.all()
    toppings = Topping.objects.all()
    sauces = Sauce.objects.all()
    


    # ✅ แปลง ID ของวัตถุดิบเป็นชื่อเมนู
    for order in pending_orders:
        order.flour = [Flour.objects.get(id=int(f)).name for f in json.loads(order.flour)]
        order.filling = [Filling.objects.get(id=int(f)).name for f in json.loads(order.filling)] if order.filling else []
        order.topping = [Topping.objects.get(id=int(t)).name for t in json.loads(order.topping)] if order.topping else []
        order.sauce = [Sauce.objects.get(id=int(s)).name for s in json.loads(order.sauce)] if order.sauce else []

    total_price = sum(order.total_price for order in pending_orders)
    total_quantity = sum(order.quantity for order in pending_orders)

    return render(request, 'cart.html', {
        "orders": pending_orders,
        "total_price": total_price,
        "total_quantity": total_quantity,
            "flours": flours,
        "fillings": fillings,
        "toppings": toppings,
        "sauces": sauces
    })


def delete_order(request, order_id):
    if request.method == "POST":
        try:
            order = get_object_or_404(Order, id=order_id)
            order.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
        

        
from django.utils.timezone import localdate

def confirm_order(request):
    if request.method == "POST":
        pending_orders = Order.objects.filter(order_group__isnull=True, user=request.user).order_by("created_at")

        if pending_orders.exists():
            today = localdate()  # วันที่ปัจจุบัน

            # ✅ ค้นหาหมายเลขคิวสูงสุดของวันนี้
            last_queue = OrderGroup.objects.filter(created_at__date=today).order_by("-queue_number").first()
            next_queue_number = (last_queue.queue_number + 1) if last_queue else 1  # ถ้ายังไม่มีออเดอร์ในวันนี้ ให้เริ่มจาก 1

            # ✅ สร้าง OrderGroup พร้อมหมายเลขคิวที่ไม่ซ้ำกันในวันนี้
            order_group = OrderGroup.objects.create(
                status="confirmed",
                queue_number=next_queue_number,
                user=request.user,
                created_at=now()  # บันทึกวันเวลาปัจจุบัน
            )

            # ✅ อัปเดต Order ให้เชื่อมกับ OrderGroup
            pending_orders.update(order_group=order_group, user=request.user)

        return JsonResponse({"status": "success", "queue_number": next_queue_number})

    return JsonResponse({"status": "error", "message": "Method Not Allowed"}, status=405)









import json
from django.shortcuts import render
from .models import Order, Flour, Filling, Topping, Sauce

def my_orders(request):
    """ ดึงคำสั่งซื้อของผู้ใช้ที่ได้รับการยืนยันหรือเสร็จสิ้น แต่ยังไม่ชำระเงิน """
    
    # ✅ ดึงเฉพาะคำสั่งซื้อที่เป็นของผู้ใช้ที่ล็อกอินอยู่ และมีสถานะ 'order_received', 'confirmed' หรือ 'completed'
    confirmed_orders = Order.objects.filter(
        order_group__status__in=['order_received', 'confirmed', 'completed'],
        user=request.user  # 🔥 เพิ่มเงื่อนไขนี้เพื่อกรองเฉพาะออเดอร์ของผู้ใช้ที่ล็อกอิน
    ).order_by('order_group__queue_number')

    # ✅ จัดกลุ่มคำสั่งซื้อโดยใช้ OrderGroup
    order_groups = {}
    for order in confirmed_orders:
        queue_number = order.order_group.queue_number
        
        if queue_number not in order_groups:
            order_groups[queue_number] = {
                "queue_number": queue_number,
                "status": order.order_group.status,
                "status_display": "",
                "total_price": 0,
                "total_quantity": 0,
                "orders": []
            }

        # ✅ แปลง ID ของวัตถุดิบให้เป็นชื่อ
        order.flour = [Flour.objects.get(id=int(f)).name for f in json.loads(order.flour)]
        order.filling = [Filling.objects.get(id=int(f)).name for f in json.loads(order.filling)] if order.filling else []
        order.topping = [Topping.objects.get(id=int(t)).name for t in json.loads(order.topping)] if order.topping else []
        order.sauce = [Sauce.objects.get(id=int(s)).name for s in json.loads(order.sauce)] if order.sauce else []

        # ✅ อัปเดตยอดรวมราคาและจำนวนสินค้า
        order_groups[queue_number]["total_price"] += order.total_price
        order_groups[queue_number]["total_quantity"] += order.quantity
        order_groups[queue_number]["orders"].append(order)

    # ✅ แปลงสถานะเป็นข้อความที่เข้าใจง่าย
    status_mapping = {
        "pending": "รอดำเนินการ",
        "order_received": "รับออเดอร์แล้ว",
        "confirmed": "กำลังดำเนินการ",
        "completed": "เสร็จสิ้น รอชำระเงิน",
        "paid": "ชำระเงินเสร็จสิ้น",
    }
    
    for queue_number, group in order_groups.items():
        group["status_display"] = status_mapping.get(group["status"], "ไม่ทราบสถานะ")

    return render(request, 'my_orders.html', {
        "formatted_orders": order_groups.values()
    })


@login_required
def logout_view(request):
    logout(request)
    return redirect("request_otp")  # เปลี่ยนเส้นทางไปยังหน้าหลักหลังจากออกจากระบบ


def profile(request):
    return render(request, 'profile.html')


def order_history(request):
    """ แสดงประวัติคำสั่งซื้อที่ชำระเงินเสร็จสิ้น """
    
    paid_orders = Order.objects.filter(order_group__status="paid").order_by("-order_group__queue_number")

    order_groups = {}
    for order in paid_orders:
        queue_number = order.order_group.queue_number

        if queue_number not in order_groups:
            order_groups[queue_number] = {
                "queue_number": queue_number,
                "status": "paid",
                "status_display": "ชำระเงินเสร็จสิ้น",
                "total_price": 0,
                "total_quantity": 0,
                "orders": []
            }

        # แปลง ID ของวัตถุดิบให้เป็นชื่อ
        order.flour = [Flour.objects.get(id=int(f)).name for f in json.loads(order.flour)]
        order.filling = [Filling.objects.get(id=int(f)).name for f in json.loads(order.filling)] if order.filling else []
        order.topping = [Topping.objects.get(id=int(t)).name for t in json.loads(order.topping)] if order.topping else []
        order.sauce = [Sauce.objects.get(id=int(s)).name for s in json.loads(order.sauce)] if order.sauce else []

        # อัปเดตราคาทั้งหมดและจำนวนสินค้า
        order_groups[queue_number]["total_price"] += order.total_price
        order_groups[queue_number]["total_quantity"] += order.quantity
        order_groups[queue_number]["orders"].append(order)

    return render(request, 'order_history.html', {
        "formatted_orders": order_groups.values()
    })




#-----------------Admin------------------------------

def Dashboard(request):
    return render(request, 'Admin/Dashboard.html')

def admin_order(request):
    order_groups = OrderGroup.objects.exclude(status="paid").order_by("queue_number")

    formatted_orders = []
    status_mapping = {
        "pending": "รอดำเนินการ",
        "order_received": "รับออเดอร์แล้ว",
        "confirmed": "กำลังดำเนินการ",
        "completed": "เสร็จสิ้น รอชำระเงิน",
        "paid": "ชำระเงินเสร็จสิ้น",
    }

    for group in order_groups:
        orders = Order.objects.filter(order_group=group)
        total_price = sum(order.total_price for order in orders)
        total_quantity = sum(order.quantity for order in orders)

        formatted_order_list = []
        for order in orders:
            formatted_order_list.append({
                "flour": [Flour.objects.get(id=int(f)).name for f in json.loads(order.flour)],
                "filling": [Filling.objects.get(id=int(f)).name for f in json.loads(order.filling)] if order.filling else [],
                "topping": [Topping.objects.get(id=int(t)).name for t in json.loads(order.topping)] if order.topping else [],
                "sauce": [Sauce.objects.get(id=int(s)).name for s in json.loads(order.sauce)] if order.sauce else [],
                "quantity": order.quantity,
                "total_price": order.total_price,
            })

        formatted_orders.append({
            "queue_number": group.queue_number,
            "status": group.status,
            "status_display": status_mapping.get(group.status, "ไม่ทราบสถานะ"),
            "total_price": total_price,
            "total_quantity": total_quantity,
            "orders": formatted_order_list,
        })

    return render(request, "Admin/admin_order.html", {"order_groups": formatted_orders})

def get_order_details(request, queue_number):
    group = get_object_or_404(OrderGroup, queue_number=queue_number)
    orders = Order.objects.filter(order_group=group)

    formatted_orders = []
    for order in orders:
        formatted_orders.append({
            "flour": [Flour.objects.get(id=int(f)).name for f in json.loads(order.flour)],
            "filling": [Filling.objects.get(id=int(f)).name for f in json.loads(order.filling)] if order.filling else [],
            "topping": [Topping.objects.get(id=int(t)).name for t in json.loads(order.topping)] if order.topping else [],
            "sauce": [Sauce.objects.get(id=int(s)).name for s in json.loads(order.sauce)] if order.sauce else [],
            "quantity": order.quantity,
            "total_price": order.total_price,
        })

    status_mapping = {
        "pending": "รอดำเนินการ",
        "order_received": "รับออเดอร์แล้ว",
        "confirmed": "กำลังดำเนินการ",
        "completed": "เสร็จสิ้น รอชำระเงิน",
        "paid": "ชำระเงินเสร็จสิ้น",
    }
    status_display = status_mapping.get(group.status, "ไม่ทราบสถานะ")

    return JsonResponse({
        "queue_number": group.queue_number,
        "status": group.status,
        "status_display": status_display,
        "total_price": sum(order.total_price for order in orders),
        "total_quantity": sum(order.quantity for order in orders),
        "orders": formatted_orders,
    })



from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Flour, Filling, Topping, Sauce

def add_menu(request):
    if request.method == "POST":
        category = request.POST.get("category")
        name = request.POST.get("name")
        price = request.POST.get("price")

        new_item = None
        if category == "flour":
            new_item = Flour.objects.create(name=name, price=price)
        elif category == "filling":
            new_item = Filling.objects.create(name=name, price=price)
        elif category == "topping":
            new_item = Topping.objects.create(name=name, price=price)
        elif category == "sauce":
            new_item = Sauce.objects.create(name=name, price=price)

        if new_item:
            return JsonResponse({
                "status": "success",
                "category": category,
                "name": new_item.name,
                "price": new_item.price
            })

        return JsonResponse({"status": "error"})

    flours = Flour.objects.all()
    fillings = Filling.objects.all()
    toppings = Topping.objects.all()
    sauces = Sauce.objects.all()

    categories = [
        {"key": "flour", "name": "แป้ง"},
        {"key": "filling", "name": "แยม"},
        {"key": "topping", "name": "ท็อปปิ้ง"},
        {"key": "sauce", "name": "ซอส"}
    ]

    return render(request, "Admin/add_menu.html", {
        "flours": flours,
        "fillings": fillings,
        "toppings": toppings,
        "sauces": sauces,
        "categories": categories
    })


def edit_menu(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        name = request.POST.get("name")
        price = request.POST.get("price")
        category = request.POST.get("category")

        if not item_id or not name or not price or not category:
            return JsonResponse({"status": "error", "message": "ข้อมูลไม่ครบถ้วน"}, status=400)

        try:
            if category == "flour":
                menu_item = get_object_or_404(Flour, id=item_id)
            elif category == "filling":
                menu_item = get_object_or_404(Filling, id=item_id)
            elif category == "topping":
                menu_item = get_object_or_404(Topping, id=item_id)
            elif category == "sauce":
                menu_item = get_object_or_404(Sauce, id=item_id)
            else:
                return JsonResponse({"status": "error", "message": "หมวดหมู่ไม่ถูกต้อง"}, status=400)

            menu_item.name = name
            menu_item.price = float(price)
            menu_item.save()

            return JsonResponse({
                "status": "success",
                "id": menu_item.id,
                "name": menu_item.name,
                "price": menu_item.price
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "ไม่รองรับ method นี้"}, status=405)

def delete_menu(request, item_id, category):
    if request.method == "POST":
        try:
            menu_item = None

            if category == "flour":
                menu_item = get_object_or_404(Flour, id=item_id)
            elif category == "filling":
                menu_item = get_object_or_404(Filling, id=item_id)
            elif category == "topping":
                menu_item = get_object_or_404(Topping, id=item_id)
            elif category == "sauce":
                menu_item = get_object_or_404(Sauce, id=item_id)
            else:
                return JsonResponse({"status": "error", "message": "หมวดหมู่ไม่ถูกต้อง"}, status=400)

            menu_item.delete()
            return JsonResponse({"status": "success", "id": item_id})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "ไม่รองรับ method นี้"}, status=405)