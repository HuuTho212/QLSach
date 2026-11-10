from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, func

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "trandinhhuuthosecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsach.db"

db.init_app(app)

class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(100),unique=True)

    def __repr__(self):
        return f"<Category {self.name} >"

class Book(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    title: Mapped[str] = mapped_column(String(100))
    author: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(default=0.0)
    quantity: Mapped[int] = mapped_column(default=0)
    category_id: Mapped[int] = mapped_column(db.ForeignKey("category.id"))
    category: Mapped["Category"] = db.relationship()
    def __repr__(self):
        return f"<Book {self.id} {self.title} >"
    
with app.app_context():
    db.create_all()

@app.get("/xem-danh-muc")
def xem_danh_muc():
    categories = db.session.scalars(
        db.select(Category).order_by(Category.name)
    ).all()
    return render_template("danh_muc.html", categories=categories)




@app.get("/them-danh-muc")
def them_danh_muc():
    return render_template("them_danh_muc.html")
@app.post("/them-danh-muc")
def them_danh_muc_post():
    name = request.form.get("name").strip()
    if not name:
        return render_template("them_danh_muc.html", message="Tên danh mục không được để trống.")
 
    if db.session.scalar(db.select(Category).where(Category.name == name)):
        return render_template("them_danh_muc.html", message=f"Danh mục {name} đã tồn tại.")
    
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    flash(f"Đã thêm danh mục {name} thành công.", "success")
    return redirect(url_for("xem_danh_muc"))



@app.get("/sua-danh-muc/<int:id>")
def sua_danh_muc(id):
    category = Category.query.get_or_404(id)
    return render_template("sua_danh_muc.html", category=category)
@app.post("/sua-danh-muc/<int:id>")
def sua_danh_muc_post(id):
    category = Category.query.get_or_404(id)
    name = request.form.get("name").strip()
    if not name:
        return render_template("sua_danh_muc.html", category=category, message="Tên danh mục không được để trống.")
 
    if db.session.scalar(db.select(Category).where(Category.name == name, Category.id != id)):
        return render_template("sua_danh_muc.html", category=category, message=f"Danh mục {name} đã tồn tại.")
    
    category.name = name
    db.session.commit()
    flash(f"Đã cập nhật danh mục {name} thành công.", "success")
    return redirect(url_for("xem_danh_muc"))



@app.post("/xoa-danh-muc/<int:id>")
def xoa_danh_muc(id):
    category = Category.query.get_or_404(id)
    so_sach = db.session.scalar(
        db.select(func.count(Book.id)).where(Book.category_id == id)
    )
    if so_sach > 0:
        flash(f"Không thể xóa danh mục {category.name} vì còn {so_sach} sách.", "danger")
        return redirect(url_for("xem_danh_muc"))
 
    db.session.delete(category)
    db.session.commit()
    flash(f"Đã xóa danh mục {category.name} thành công.", "success")
    return redirect(url_for("xem_danh_muc"))



@app.get("/xem-sach")
def xem_sach():
    category_id = request.args.get("category_id", type=int)
    query = db.select(Book).order_by(Book.title)
    if category_id:
        query = query.where(Book.category_id == category_id)
    books = db.session.scalars(query).all()
    categories = db.session.scalars(
        db.select(Category).order_by(Category.name)
    ).all()
    return render_template("sach.html", books=books, categories=categories, category_id=category_id)




@app.get("/them-sach")
def them_sach():
    categories = db.session.scalars(
        db.select(Category).order_by(Category.name)
    ).all()
    return render_template("them_sach.html", categories=categories)
@app.post("/them-sach")
def them_sach_post():
    categories = db.session.scalars(
        db.select(Category).order_by(Category.name)
    ).all()
    title = request.form.get("title").strip()
    author = request.form.get("author").strip()
    price = request.form.get("price").strip()
    quantity = request.form.get("quantity").strip()
    category_id = request.form.get("category_id", "").strip()
 
    if not title or not author or not price or not quantity or not category_id:
        return render_template("them_sach.html", categories=categories, message="Các trường không được để trống.")
    
    try:
        price = float(price)
        quantity = int(quantity)
        category_id = int(category_id)
    except ValueError:
        return render_template("them_sach.html", categories=categories, message="Giá, số lượng và danh mục phải là số hợp lệ.")
 
    if db.session.get(Category, category_id) is None:
        return render_template("them_sach.html", categories=categories, message="Danh mục không tồn tại.")
    
    book = Book(title=title, author=author, price=price, quantity=quantity, category_id=category_id)
    db.session.add(book)
    db.session.commit()
    flash(f"Đã thêm sách {title} thành công.", "success")
    return redirect(url_for("xem_sach"))



@app.get("/sua-sach/<int:id>")
def sua_sach(id):
    book = Book.query.get_or_404(id)
    categories = db.session.scalars(
        db.select(Category).order_by(Category.name)
    ).all()
    return render_template("sua_sach.html", book=book, categories=categories)
@app.post("/sua-sach/<int:id>")
def sua_sach_post(id):
    book = Book.query.get_or_404(id)
    categories = db.session.scalars(
        db.select(Category).order_by(Category.name)
    ).all()
    title = request.form.get("title").strip()
    author = request.form.get("author").strip()
    price = request.form.get("price").strip()
    quantity = request.form.get("quantity").strip()
    category_id = request.form.get("category_id", "").strip()
 
    if not title or not author or not price or not quantity or not category_id:
        return render_template("sua_sach.html", book=book, categories=categories, message="Các trường không được để trống.")
    
    try:
        price = float(price)
        quantity = int(quantity)
        category_id = int(category_id)
    except ValueError:
        return render_template("sua_sach.html", book=book, categories=categories, message="Giá, số lượng và danh mục phải là số hợp lệ.")
 
    if db.session.get(Category, category_id) is None:
        return render_template("sua_sach.html", book=book, categories=categories, message="Danh mục không tồn tại.")
    
    book.title = title
    book.author = author
    book.price = price
    book.quantity = quantity
    book.category_id = category_id
    db.session.commit()
    flash(f"Đã cập nhật sách {title} thành công.", "success")
    return redirect(url_for("xem_sach"))



@app.post("/xoa-sach/<int:id>")
def xoa_sach(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash(f"Đã xóa sách {book.title} thành công.", "success")
    return redirect(url_for("xem_sach"))


@app.get("/")
@app.get("/dashboard")
def dashboard():
    tong_danh_muc = db.session.scalar(db.select(func.count(Category.id)))
    tong_sach = db.session.scalar(db.select(func.count(Book.id)))
    sach_theo_danh_muc = db.session.execute(
        db.select(Category.id, Category.name, func.count(Book.id))
        .outerjoin(Book, Book.category_id == Category.id)
        .group_by(Category.id, Category.name)
        .order_by(Category.name)
    ).all()
    return render_template(
        "dashboard.html",
        tong_danh_muc=tong_danh_muc,
        tong_sach=tong_sach,
        sach_theo_danh_muc=sach_theo_danh_muc,
    )

if __name__ == "__main__":
    app.run(debug=True)