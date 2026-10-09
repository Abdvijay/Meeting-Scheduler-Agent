from trigger import check_for_new_email


email = check_for_new_email()


if email:

    print("\nTRIGGER RESULT")
    print("--------------")

    print(
        "Agent can now start processing the email."
    )

else:

    print(
        "\nAgent will not start."
    )