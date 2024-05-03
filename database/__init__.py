# __init.py__ for database package
from database.about_page import (
    open_login,
    open_user,
    open_database,
    main
)
from database.camera_webcam import (
    error_message_box,
    get_filename,
    set_has_image,
    has_a_image,
    stop_webcam,
    start_webcam,
    snapshot,
    show_frame,
    camera_status
)
from database.createuser_page import (
    make_user_database,
    hash_password,
    add_user_data,
    is_valid_email,
    is_password_strong,
    create_account,
    open_login_window,
    create_user
)
from database.database_page import (
    open_user_window,
    open_login_window,
    open_about,
    browse_files,
    get_frame_img,
    delete_image_of_person,
    get_photo_folder,
    back,
    forward,
    jump_to_photo,
    upload_to_insta,
    insta_popup,
    upload_cloud_file,
    make_frame_btns,
    make_frame,
    main
)
from database.forgotpassword_page import (
    find_user_email,
    send_reset_email,
    is_valid_email,
    handle_forgot_password,
    open_login_window,
    forgot_user
)
from database.login_page import (
    make_user_database,
    verify_credentials,
    clear_frame,
    open_user_window,
    open_create_user_window,
    open_forgot_password_window,
    error_message_box,
    create_main_page,
    main
)
from database.user_page import (
    open_database,
    open_login,
    open_about,
    message_box,
    set_filename,
    browse_files,
    create_caricature,
    get_main_frame,
    check_snapshot,
    webcam_view,
    show_images_frame,
    show_main_page_frame,
    main
)