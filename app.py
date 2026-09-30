import streamlit as st
import pandas as pd

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Tính lãi tiền gửi tiết kiệm",
    page_icon="💰",
    layout="centered"
)

# =========================
# HÀM ĐỊNH DẠNG TIỀN
# =========================
def format_vnd(value):
    return f"{value:,.0f} VNĐ".replace(",", ".")


# =========================
# TIÊU ĐỀ
# =========================
st.title("💰 TÍNH LÃI TIỀN GỬI TIẾT KIỆM")
st.write(
    "Ứng dụng tính toán tiền lãi theo **lãi đơn** hoặc **lãi kép** "
    "với nhiều hình thức nhận lãi."
)

st.divider()

# =========================
# NHẬP THÔNG TIN
# =========================

st.subheader("📋 Thông tin tiền gửi")

tien_gui = st.number_input(
    "Số tiền gửi (VNĐ)",
    min_value=0.0,
    value=100_000_000.0,
    step=1_000_000.0,
    format="%.0f"
)

ky_han = st.number_input(
    "Kỳ hạn (tháng)",
    min_value=1,
    max_value=600,
    value=12,
    step=1
)

lai_suat = st.number_input(
    "Lãi suất (%/năm)",
    min_value=0.0,
    max_value=100.0,
    value=6.0,
    step=0.1
)

loai_lai = st.selectbox(
    "Phương pháp tính lãi",
    [
        "Lãi đơn",
        "Lãi kép"
    ]
)

hinh_thuc = st.selectbox(
    "Hình thức nhận lãi",
    [
        "Lãnh lãi hàng tháng",
        "Lãnh lãi hàng quý",
        "Lãnh lãi cuối kỳ"
    ]
)

st.divider()

# =========================
# NÚT TÍNH TOÁN
# =========================

if st.button("🧮 TÍNH LÃI", type="primary", use_container_width=True):

    if tien_gui <= 0:
        st.error("Vui lòng nhập số tiền gửi lớn hơn 0.")
        st.stop()

    if lai_suat < 0:
        st.error("Lãi suất không được nhỏ hơn 0.")
        st.stop()

    # Lãi suất năm chuyển thành số thập phân
    lai_nam = lai_suat / 100

    # Thời gian gửi tính theo năm
    so_nam = ky_han / 12

    # Xác định số tháng của một kỳ nhận lãi
    if hinh_thuc == "Lãnh lãi hàng tháng":
        thang_moi_ky = 1

    elif hinh_thuc == "Lãnh lãi hàng quý":
        thang_moi_ky = 3

    else:
        thang_moi_ky = ky_han

    # =========================
    # TRƯỜNG HỢP LÃNH CUỐI KỲ
    # =========================

    if hinh_thuc == "Lãnh lãi cuối kỳ":

        if loai_lai == "Lãi đơn":
            tong_lai = tien_gui * lai_nam * so_nam
            tong_tien = tien_gui + tong_lai

        else:
            # Số kỳ ghép lãi theo tháng
            so_ky = ky_han

            lai_ky = lai_nam / 12

            tong_tien = tien_gui * (1 + lai_ky) ** so_ky
            tong_lai = tong_tien - tien_gui

        lai_dinh_ky = tong_lai

        so_ky_hien_thi = 1

        bang_du_lieu = pd.DataFrame({
            "Kỳ": [f"Cuối kỳ ({ky_han} tháng)"],
            "Số dư đầu kỳ": [tien_gui],
            "Tiền lãi": [tong_lai],
            "Số dư cuối kỳ": [tong_tien]
        })

    # =========================
    # LÃNH LÃI HÀNG THÁNG / QUÝ
    # =========================

    else:

        # Số kỳ nhận lãi
        so_ky = ky_han // thang_moi_ky

        # Lãi suất cho mỗi kỳ
        lai_ky = lai_nam * thang_moi_ky / 12

        du_no = tien_gui
        tong_lai = 0

        danh_sach = []

        for i in range(1, so_ky + 1):

            so_du_dau = du_no

            if loai_lai == "Lãi đơn":
                tien_lai_ky = tien_gui * lai_ky

                # Với lãi đơn, tiền lãi không nhập vào vốn
                so_du_cuoi = du_no

            else:
                tien_lai_ky = du_no * lai_ky

                # Lãi kép: tiền lãi nhập vào vốn
                du_no = du_no + tien_lai_ky
                so_du_cuoi = du_no

            tong_lai += tien_lai_ky

            danh_sach.append({
                "Kỳ": i,
                "Số dư đầu kỳ": so_du_dau,
                "Tiền lãi": tien_lai_ky,
                "Số dư cuối kỳ": so_du_cuoi
            })

        tong_tien = tien_gui + tong_lai

        lai_dinh_ky = tong_lai / so_ky

        bang_du_lieu = pd.DataFrame(danh_sach)

    # =========================
    # KẾT QUẢ
    # =========================

    st.success("✅ Đã tính toán thành công!")

    st.subheader("📊 Kết quả")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "💵 Tiền lãi định kỳ",
            format_vnd(lai_dinh_ky)
        )

    with col2:
        st.metric(
            "📈 Tổng tiền lãi",
            format_vnd(tong_lai)
        )

    with col3:
        st.metric(
            "💰 Tổng gốc + lãi",
            format_vnd(tong_tien)
        )

    st.divider()

    # =========================
    # THÔNG TIN TÓM TẮT
    # =========================

    st.subheader("📝 Thông tin khoản tiền gửi")

    thong_tin = pd.DataFrame({
        "Thông tin": [
            "Số tiền gửi",
            "Kỳ hạn",
            "Lãi suất",
            "Phương pháp tính",
            "Hình thức nhận lãi"
        ],
        "Giá trị": [
            format_vnd(tien_gui),
            f"{ky_han} tháng",
            f"{lai_suat:.2f}%/năm",
            loai_lai,
            hinh_thuc
        ]
    })

    st.table(thong_tin)

    # =========================
    # BẢNG CHI TIẾT
    # =========================

    st.subheader("📅 Chi tiết tiền lãi theo từng kỳ")

    bang_hien_thi = bang_du_lieu.copy()

    bang_hien_thi["Số dư đầu kỳ"] = (
        bang_hien_thi["Số dư đầu kỳ"]
        .apply(format_vnd)
    )

    bang_hien_thi["Tiền lãi"] = (
        bang_hien_thi["Tiền lãi"]
        .apply(format_vnd)
    )

    bang_hien_thi["Số dư cuối kỳ"] = (
        bang_hien_thi["Số dư cuối kỳ"]
        .apply(format_vnd)
    )

    st.dataframe(
        bang_hien_thi,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # GIẢI THÍCH
    # =========================

    with st.expander("📚 Giải thích cách tính"):

        if loai_lai == "Lãi đơn":

            st.markdown("""
            **Lãi đơn** là phương pháp trong đó tiền lãi phát sinh
            không được cộng vào tiền gốc để tiếp tục sinh lãi.

            Công thức:

            **Tiền lãi = Tiền gốc × Lãi suất × Thời gian**

            Vì vậy, tiền lãi của mỗi kỳ được tính dựa trên
            số tiền gốc ban đầu.
            """)

        else:

            st.markdown("""
            **Lãi kép** là phương pháp trong đó tiền lãi của mỗi kỳ
            được cộng vào tiền gốc và tiếp tục sinh lãi ở các kỳ sau.

            Công thức tổng quát:

            **A = P × (1 + r)ⁿ**

            Trong đó:

            - **P**: số tiền gốc ban đầu
            - **r**: lãi suất mỗi kỳ
            - **n**: số kỳ tính lãi
            - **A**: tổng số tiền nhận được
            """)

    # =========================
    # GHI CHÚ
    # =========================

    st.info(
        "ℹ️ Kết quả trên là mô phỏng theo công thức toán học. "
        "Lãi suất thực tế của ngân hàng có thể áp dụng các quy định, "
        "cách làm tròn và điều kiện sản phẩm tiền gửi riêng."
    )


# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "Ứng dụng tính lãi tiền gửi tiết kiệm | Streamlit"
)
