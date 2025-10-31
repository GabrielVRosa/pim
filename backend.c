#include <stdio.h>
#include <string.h>

typedef struct {
    char login[50];   // Nome de login do usuário
    char senha[50];   // Senha do usuário
    char tipo[20];    // Tipo (admin ou teacher)
    char materia[50]; // Matéria associada
} Usuario;

//estrutura que representa um aluno do sistema
typedef struct {
    char ra[20];
    char nome[50];
    char senha[20];
    char turma[20];
    char notas[1000];
} Aluno;

Usuario usuarios[100];
int total_usuarios = 0;


Aluno alunos[100];
int total_alunos = 0;  //quantos alunos estão cadastrados


__declspec(dllexport) void init_backend() {
    total_usuarios = 0;
    total_alunos = 0;

    //cria o usuário padrão (admin/admin)
    strcpy(usuarios[total_usuarios].login, "admin");
    strcpy(usuarios[total_usuarios].senha, "admin");
    strcpy(usuarios[total_usuarios].tipo, "admin");
    strcpy(usuarios[total_usuarios].materia, "");
    total_usuarios++;
}


/*
    função: add_user
    adiciona um novo usuário (professor ou adm)
*/
__declspec(dllexport) int add_user(const char* login, const char* senha, const char* tipo, const char* materia){
    strcpy(usuarios[total_usuarios].login, login);
    strcpy(usuarios[total_usuarios].senha, senha);
    strcpy(usuarios[total_usuarios].tipo, tipo);
    strcpy(usuarios[total_usuarios].materia, materia);
    total_usuarios++;
    return 1; // 1 = sucesso
}


/*
    função: check_user
    verifica se o login e senha de um usuário são válidos
    retorna 1 se for válido e 0 se não for
*/
__declspec(dllexport) int check_user(const char* login, const char* senha, char* tipo, int tamanho){
    for(int i=0; i<total_usuarios; i++){
        if(strcmp(usuarios[i].login, login)==0 && strcmp(usuarios[i].senha, senha)==0){
            strncpy(tipo, usuarios[i].tipo, tamanho);
            return 1;
        }
    }
    tipo[0] = '\0';
    return 0; // reetorna 0 quando o usuario for inválido
}


/*
    função: get_professor_subject
    retorna a matéria associada a um professor (pelo login)
*/
__declspec(dllexport) int get_professor_subject(const char* login, char* materia, int tamanho){
    for(int i=0; i<total_usuarios; i++){
        if(strcmp(usuarios[i].login, login)==0 && strcmp(usuarios[i].tipo,"teacher")==0){
            strncpy(materia, usuarios[i].materia, tamanho);
            return 1; // retorna 1 caso o professor seja encontrado no sistema
        }
    }
    materia[0]='\0'; // 0 caso nao encontre o prof
    return 0;
}


/*
    função: add_student
    cadastra um novo aluno com RA, nome, senha e turma
*/
__declspec(dllexport) int add_student(const char* ra, const char* nome, const char* senha, const char* turma){
    strcpy(alunos[total_alunos].ra, ra);
    strcpy(alunos[total_alunos].nome, nome);
    strcpy(alunos[total_alunos].senha, senha);
    strcpy(alunos[total_alunos].turma, turma);
    alunos[total_alunos].notas[0] = '\0';
    total_alunos++;
    return 1;
}


/*
    função: get_student_name
    retorna o nome do aluno com base em seu RA
*/
__declspec(dllexport) int get_student_name(const char* ra, char* nome, int tamanho){
    for(int i=0; i<total_alunos; i++){
        if(strcmp(alunos[i].ra, ra)==0){
            strncpy(nome, alunos[i].nome, tamanho);
            return 1; // retorna 1 quando encontra um aluno
        }
    }
    nome[0] = '\0'; // caso contrario 0
    return 0;
}


/*
    função: check_student
    verifica se o RA e a senha do aluno são válidos
*/
__declspec(dllexport) int check_student(const char* ra, const char* senha){
    for(int i=0; i<total_alunos; i++){
        if(strcmp(alunos[i].ra, ra)==0 && strcmp(alunos[i].senha, senha)==0){
            return 1; // 1 para loginb valido
        }
    }
    return 0; // 0 caso invalido
}


/*
    função: register_grade
    registra uma nota para um aluno em uma determinada matéria
*/
__declspec(dllexport) int register_grade(const char* ra, const char* materia, double nota){
    for(int i=0; i<total_alunos; i++){
        if(strcmp(alunos[i].ra, ra)==0){
            char buffer[50];
            sprintf(buffer, "%s:%.2f;", materia, nota);
            strcat(alunos[i].notas, buffer); // Adiciona ao campo notas
            return 1;
        }
    }
    return 0;
}


/*
    função: get_student_grades
    retorna todas as notas de um aluno (em formato de texto).
*/
__declspec(dllexport) int get_student_grades(const char* ra, char* buffer, int tamanho){
    for(int i=0; i<total_alunos; i++){
        if(strcmp(alunos[i].ra, ra)==0){
            strncpy(buffer, alunos[i].notas, tamanho);
            return 1; // caso o aluno tenha alguma nota ja registrada o valor sera retornado como 1
        }
    }
    buffer[0] = '\0'; // caso contrario 0
    return 0;
}


/*
    função: get_class_grades
    retorna as notas de todos os alunos de uma turma
    se 'turma' for vazia, ele vai retornar as notas de todos os alunos
*/
__declspec(dllexport) int get_class_grades(const char* turma, char* buffer, int tamanho){
    buffer[0] = '\0';

    for(int i=0; i<total_alunos; i++){
        if(strlen(turma) == 0 || strcmp(alunos[i].turma, turma) == 0){
            char linha[2000];
            sprintf(linha, "%s:%s;", alunos[i].ra, alunos[i].notas);
            strcat(buffer, linha);
        }
    }
    return 1;
}